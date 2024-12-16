from sys import exc_info

from flask import app, current_app
import os
from flaskr.db import get_db
import time
from threading import Thread, Event
from datetime import datetime, timedelta
from flaskr.utils.logger import Logger
from flaskr.hardware.hardware_base import HardwareRelay
import json
import redis


# TODO: make here base class to store in hardware collection

class VentilationTaskThread(Thread):
    """

    """
    def __init__(self, app_context, name="worker:ventilation"):
        super().__init__()
        with app_context:
            self.app_context = app_context

            self.redis_client = get_db()
            self.kill_event = Event()
            self.daemon = True  # Ensures the thread stops when the main program exits
            # Redis keys for commands and task state
            pid = os.getpid()
            prefix = name if name else "worker:ventilation"
            self.COMMAND_KEY = f"{prefix}:user_command"
            self.COMMAND_ARGS_KEY = f"{prefix}:command_args"
            self.TASK_LOCK_KEY = f"{prefix}:lock"
            self.TASK_PID_KEY = f"{prefix}:pid"
            self.TASK_PARAMS = f"{prefix}:params"
            self.TASK_STAGES = f"{prefix}:stages"
            self.TASK_COMMANDS = f"{prefix}:commands"
            self.logger = Logger.get_logger(f"{prefix}_{pid}")


            # Attempt to acquire lock
            if self.redis_client.set(self.TASK_LOCK_KEY, "locked", nx=True, ex=10):
                self.redis_client.set(self.TASK_PID_KEY, pid)

                self.logger.info(f"{prefix} started with PID {pid}")
            else:
                self.logger.info("Ventilation task is already running. Exiting worker.")
                return

            # create drivers
            # YES, THEY ARE HARDCODED
            self.relay_0: HardwareRelay = current_app.global_hardware_collection.hardware[101]
            self.relay_1: HardwareRelay = current_app.global_hardware_collection.hardware[102]
            self.relay_2: HardwareRelay = current_app.global_hardware_collection.hardware[103]
            self.relay_3: HardwareRelay = current_app.global_hardware_collection.hardware[104]


            # stages and numbers for future
            self.stages = {
                0: "idle",
                1: "part1",
                2: "part2",
                3: "part3",
                4: "part4"
            }
            self.commands = {
                "start": "Run task from current step",
                "stop": "Stop task on current step",
                "ping": "Dump info about that task to redis now",
                "reset": "Set current task to 0 and stop",
                "kill": "Kill task and exit"
            }
            # define params
            self.params = {
                "last_user_command": None,
                "last_response": datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
                "type": "task",
                "name": prefix,
                "pid": pid,
                "step": 0,
                "running": False,
                "current_stage_name": self.stages[0]
            }
            self.data = {}

        # save it all to redis first time
        self._write_status()


    def _write_status(self):
        """Write the current step and timestamp to Redis."""
        self.redis_client.set(self.TASK_PARAMS, json.dumps(self.params))
        self.redis_client.set(self.TASK_COMMANDS, json.dumps(self.commands))
        self.redis_client.set(self.TASK_STAGES, json.dumps(self.stages))

    # def _write_ping(self):
    #     """Write a ping message to Redis to show the task is alive."""
    #     self.redis_client.set('task_ping', time.time())

    def main_work(self, step):
        """The main work of the task, divided into steps."""
        # make one step and exit
        with self.app_context:
            if self.params["running"] and not self.kill_event.is_set():
                if step == 0:
                    self.logger.info("step 0 - idle")
                    self.relay_0.turn_off()
                    self.relay_1.turn_off()
                    self.relay_2.turn_off()
                    self.relay_3.turn_off()
                    # Just sleep for 10 seconds
                    time.sleep(10)  # Example work duration
                    self.params["step"] += 1
                elif step == 1:
                    self.logger.info("step 1")
                    self.relay_0.turn_on()
                    time.sleep(5)
                    self.params["step"] += 1
                elif step == 2:
                    self.logger.info("step 2")
                    self.relay_1.turn_on()
                    time.sleep(5)
                    self.params["step"] += 1
                elif step == 3:
                    self.logger.info("step 3")
                    self.relay_2.turn_on()
                    time.sleep(5)
                    self.params["step"] += 1
                elif step == 4:
                    self.logger.info("step 4")
                    self.relay_3.turn_on()
                    time.sleep(5)
                    self.params["step"] = 0


                # finally update params
                self.params["last_response"] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                self.params["current_stage_name"] = self.stages[self.params["step"]]
                self._write_status()


    def run(self):
        """The task's thread main loop."""
        while not self.kill_event.is_set():
            # infinite loop
            try:
                # first - read new user command
                command = self.redis_client.get(self.COMMAND_KEY)
                if command:
                    self.params["last_user_command"] = command
                if command == "start" and not self.params["running"] :
                    self.redis_client.delete(self.COMMAND_KEY)  # Clear the command
                    self.params["running"] = True
                    self.logger.info(f"start work from step {self.params["step"]}")
                elif command == "stop" and self.params["running"] :
                    self.redis_client.delete(self.COMMAND_KEY)  # Clear the command
                    self.params["running"] = False
                    self.logger.info(f"stop vent task at step {self.params["step"]}")
                elif command == "reset":
                    self.redis_client.delete(self.COMMAND_KEY)
                    self.params["step"] = 0
                    self.params["running"] = False
                    self.logger.info("set current step to 0 and stop")
                elif command == "ping":
                    self.redis_client.delete(self.COMMAND_KEY)
                    self._write_status()
                    self.logger.info("pong")
                elif command == "kill":
                    self.redis_client.delete(self.COMMAND_KEY)
                    self.kill_event.set()

                # after command checking - work
                self.main_work(self.params["step"])
            except Exception as e:
                self.logger.error(f"Error in task loop: {e}", exc_info=True)
            self._write_status()
            time.sleep(1)  # Periodic check for new commands

    def kill(self):
        """Stop the thread gracefully from outside."""
        self.kill_event.set()

    def stop(self):
        """Stop the thread gracefully from outside."""
        self.params["running"] = False

    @classmethod
    def read_task_data(cls, redis_client, task_prefix="worker:ventilation"):
        """
        Reads and returns all data about the task from Redis.

        :param redis_client: Redis connection instance
        :param task_prefix: Prefix for Redis keys related to the task
        :return: Dictionary containing task params, commands, and stages
        """
        try:
            params = redis_client.get(f"{task_prefix}:params")
            commands = redis_client.get(f"{task_prefix}:commands")
            stages = redis_client.get(f"{task_prefix}:stages")

            # Parse JSON strings to dictionaries
            task_data = {
                "params": json.loads(params) if params else {},
                "commands": json.loads(commands) if commands else {},
                "stages": json.loads(stages) if stages else {},
                "data": {}    # aaaaaaaaaaaaaaaaaaaaa
            }
            return task_data
        except Exception as e:
            Logger.get_logger("fuuuu").error(f"error getting task data{e}", exc_info=True)
            return {}

    @classmethod
    def write_task_command(cls, redis_client, task_prefix="worker:ventilation", command=None, args=None):
        """
        Writes a command and optional arguments to Redis for the task.

        :param redis_client: Redis connection instance
        :param task_prefix: Prefix for Redis keys related to the task
        :param command: Command to write (e.g., "start", "stop", "reset", "kill", "ping")
        :param args: Optional arguments for the command
        """
        try:
            if command:
                redis_client.set(f"{task_prefix}:user_command", command)
            if args:
                redis_client.set(f"{task_prefix}:command_args", json.dumps(args))
            Logger.get_logger("fuuuu").info(f"command {command} for task {task_prefix} is written to redis")
        except Exception as e:
            Logger.get_logger("fuuuu").error(f"error writing task command: {e}", exc_info=True)






# def read_task_data(redis_host='localhost', redis_port=6379, task_prefix="worker:ventilation"):
#     """
#     Reads and returns all data about the task from Redis.
#
#     :param redis_host: Redis server hostname
#     :param redis_port: Redis server port
#     :param task_prefix: Prefix for Redis keys related to the task
#     :return: Dictionary containing task params, commands, and stages
#     """
#     redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
#
#     try:
#         params = redis_client.get(f"{task_prefix}:params")
#         commands = redis_client.get(f"{task_prefix}:commands")
#         stages = redis_client.get(f"{task_prefix}:stages")
#
#         # Parse JSON strings to dictionaries
#         task_data = {
#             "params": json.loads(params) if params else {},
#             "commands": json.loads(commands) if commands else {},
#             "stages": json.loads(stages) if stages else {}
#         }
#         return task_data
#     except Exception as e:
#         Logger.get_logger("fuuuu").error(f"error getting task data{e}", exc_info=True)
#         return {}
#
# def write_task_command(command, args=None, redis_host='localhost', redis_port=6379, task_prefix="worker:ventilation"):
#     """
#     Writes a command and optional arguments to Redis for the task.
#
#     :param command: Command to write (e.g., "start", "stop", "reset", "kill", "ping")
#     :param args: Optional arguments for the command
#     :param redis_host: Redis server hostname
#     :param redis_port: Redis server port
#     :param task_prefix: Prefix for Redis keys related to the task
#     """
#     redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
#
#     try:
#         redis_client.set(f"{task_prefix}:user_command", command)
#         if args:
#             redis_client.set(f"{task_prefix}:command_args", json.dumps(args))
#         print(f"Command '{command}' written to Redis.")
#     except Exception as e:
#         print(f"Error writing task command: {e}")



if __name__ == "__main__":
    pass
    # now = datetime(2024, 3, 31, 23, 57, 54, 720267)
    # now = datetime.now()
    # now = now.replace(second=0, microsecond=0)
    # next_run_minute = ((now.minute // 15) + 1) * 15
    # delta_minutes = next_run_minute - now.minute
    # next_run_time = now + timedelta(minutes=delta_minutes)
    # print(f"Scheduling next run at {next_run_time}")
    redis_host = 'localhost'
    redis_port = 6379
    task_prefix = "worker:ventilation"
    redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
    VentilationTaskThread.write_task_command(redis_client, task_prefix, "start")
    task_data = VentilationTaskThread.read_task_data(redis_client, task_prefix)
    print(json.dumps(task_data, indent=4))
    # time.sleep(10)
    # task_data = VentilationTaskThread.read_task_data()
    # print(json.dumps(task_data, indent=4))

