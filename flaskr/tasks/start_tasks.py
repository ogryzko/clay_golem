import redis
import rq
from flask import current_app
from ..tasks.data_logger_cycle import update_device_data
from ..tasks.ventilation_loop import ventilation_loop
import click


@click.command('start-tasks')
def start_tasks_command():
    # # start redis queue tasks for data logging and lss control loop
    red = redis.Redis(host='localhost', port=6379)

    # try to get lock to check if tasks already queued
    if red.set("lock:tasks_started", "test", ex=10, nx=True):
        db_path = current_app.instance_path + "/" + current_app.config['DATA_DB_NAME']
        queue = rq.Queue(connection=red)
        # tasks for update devices states in redis
        queue.enqueue(update_device_data, current_app.config, db_path, current_app.config['RELAY_1_DICT'], 'localhost', 6379, "default")
        queue.enqueue(update_device_data, current_app.config, db_path, current_app.config['RELAY_2_DICT'], 'localhost', 6379, "default")
        queue.enqueue(update_device_data, current_app.config, db_path, current_app.config['RELAY_3_DICT'], 'localhost', 6379, "default")
        queue.enqueue(update_device_data, current_app.config, db_path, current_app.config['RELAY_4_DICT'], 'localhost', 6379, "default")
        queue.enqueue(update_device_data, current_app.config, db_path, current_app.config['SENSOR_DHT22_1_DICT'], 'localhost', 6379,
                      "default")
        queue.enqueue(update_device_data, current_app.config, db_path, current_app.config['SENSOR_DS18B20_1_DICT'], 'localhost', 6379,
                      "default")

        # create redis queue workers for that work
        workers = []
        for i in range(8):
            wi = rq.Worker(['default'], connection=red)
            workers.append(wi)
            wi.work()

        # also creating one scheduled worker
        worker = rq.Worker(queues=['default'], connection=red)
        worker.work(with_scheduler=True)


def init_tasks(app):
    app.cli.add_command(start_tasks_command)