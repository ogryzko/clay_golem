from flaskr.tasks.rq_tasks import short_task, short_periodical_task
from flaskr.tasks.data_logger_cycle import update_device_data
from flaskr.tasks.ventilation_loop import ventilation_loop
from flask import current_app
import rq
import sys
import datetime
import redis

sys.path.append("/home/bigfoot/PycharmProjects/clay_golem/instance")
import config


if __name__ == "__main__":
    r = redis.Redis(host='localhost', port=6379)
    queue = rq.Queue(connection=r)
    # tasks for update devices states in redis
    queue.enqueue(update_device_data, config.RELAY_1_DICT, 'localhost', 6379, "default")
    queue.enqueue(update_device_data, config.RELAY_2_DICT, 'localhost', 6379, "default")
    queue.enqueue(update_device_data, config.RELAY_3_DICT, 'localhost', 6379, "default")
    queue.enqueue(update_device_data, config.RELAY_1_DICT, 'localhost', 6379, "default")
    queue.enqueue(update_device_data, config.SENSOR_DHT22_1_DICT, 'localhost', 6379, "default")
    queue.enqueue(update_device_data, config.SENSOR_DS18B20_1_DICT, 'localhost', 6379, "default")

    # schedule task to every 6 minutes ventilation
    now = datetime.datetime.now()
    now = now.replace(second=0, microsecond=0)
    next_run_minute = ((now.minute // 6) + 1) * 6
    delta_minutes = next_run_minute - now.minute
    next_run_time = now + datetime.timedelta(minutes=delta_minutes)
    queue.enqueue_at(next_run_time, ventilation_loop, 'localhost', 6379, "default")


    # NOTE  !!!!
    # before run rq worker in console you need to run
    # export PYTHONPATH="/home/bigfoot/PycharmProjects/clay_golem/flaskr"
    # and ALL imports must start from flaskr.smth.smth ...
    # else it will crash



    # init_tasks()
    # start two new workers and sleep forever
    # w = rq.Worker(['default'], connection=r)
    # w_sch = rq.Worker(['default'], connection=r)
    # w_sch.work(with_scheduler=True)
    # w.work()

