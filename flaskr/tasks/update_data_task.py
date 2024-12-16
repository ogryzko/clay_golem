import sys
from logging import exception

sys.path.insert(0, "/opt/clay/clay_golem")
from flaskr.db import get_db
from flask import current_app
import os
import time
from flaskr.utils.logger import Logger

def state_update_worker():
    """
    That worker must be run only once. For that purpose we have lock in redis.
    """
    with current_app.app_context():
        pid = os.getpid()
        redis_client = get_db()
        # Redis keys for commands and task state
        prefix = f"worker:state_update"
        COMMAND_KEY = f"{prefix}:command"
        COMMAND_ARGS_KEY = f"{prefix}:command_args"
        TASK_LOCK_KEY = f"{prefix}:lock"
        TASK_PID_KEY = f"{prefix}:pid"
        logger = Logger.get_logger(f"state_update_worker_{pid}")
        try:
            # Attempt to acquire lock
            if redis_client.set(TASK_LOCK_KEY, "locked", nx=True, ex=10):
                redis_client.set(TASK_PID_KEY, pid)
                logger.info(f"Worker started with PID {pid}")
            else:
                logger.info("Task is already running. Exiting worker.")
                return

            while True:
                logger.info("Trying to load state updates from real devices.")
                current_app.global_hardware_collection.update_all_hardware_info()
                time.sleep(1)

        except Exception as e:
            logger.error(f"Worker with PID {pid} exited with error {e}", exc_info=True)

        finally:
            # Release lock and clean up
            if redis_client.get(TASK_PID_KEY) == str(pid):
                redis_client.delete(TASK_LOCK_KEY)
                redis_client.delete(TASK_PID_KEY)
            logger.info(f"Worker with PID {pid} exited")

def one_device_update_worker(app_context, device_id):
    """
    That worker must be run only once. Fo that purpose we have lock in redis.
    """
    with app_context:
        pid = os.getpid()
        redis_client = get_db()
        # Redis keys for commands and task state
        prefix = f"worker_{device_id}:"
        COMMAND_KEY = f"{prefix}:state_update_command"
        COMMAND_ARGS_KEY = f"{prefix}:state_update_command_args"
        TASK_LOCK_KEY = f"{prefix}:state_update"
        TASK_PID_KEY = f"{prefix}:state_update_pid"
        logger = Logger.get_logger(f"state_update_worker_{pid}")
        try:
            # Attempt to acquire lock
            if redis_client.set(TASK_LOCK_KEY, "locked", nx=True, ex=10):
                redis_client.set(TASK_PID_KEY, pid)
                logger.info(f"Worker started with PID {pid}")
            else:
                logger.info("Task is already running. Exiting worker.")
                return

            while True:
                logger.info("Trying to load state updates from real devices.")
                current_app.global_hardware_collection.update_all_hardware_info()
                time.sleep(1)

        except Exception as e:
            logger.error(f"Worker with PID {pid} exited with error {e}", exc_info=True)

        finally:
            # Release lock and clean up
            if redis_client.get(TASK_PID_KEY) == str(pid):
                redis_client.delete(TASK_LOCK_KEY)
                redis_client.delete(TASK_PID_KEY)
            logger.info(f"Worker with PID {pid} exited")
