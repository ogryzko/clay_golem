import redis
import rq
from rq.command import send_shutdown_command, send_kill_horse_command, send_stop_job_command
from flask import current_app
from ..tasks.data_logger_cycle import update_device_data
from ..tasks.ventilation_loop import ventilation_loop, calculate_next_loop_time
import click
from rq.registry import FailedJobRegistry, ScheduledJobRegistry, StartedJobRegistry
import datetime


@click.command('start-tasks')
def start_tasks_command():
    # # start redis queue tasks for data logging and lss control loop
    red = redis.Redis(host='localhost', port=6379)

    # try to get lock to check if tasks already queued
    if red.set("lock:tasks_started", "test", ex=10, nx=True):
        db_path = current_app.instance_path + "/" + current_app.config['DATA_DB_NAME']
        queue = rq.Queue(connection=red)
        # tasks for update devices states in redis
        queue.enqueue(update_device_data, current_app.config, db_path, 'RELAY_1_DICT')
        queue.enqueue(update_device_data, current_app.config, db_path, 'RELAY_2_DICT')
        queue.enqueue(update_device_data, current_app.config, db_path, 'RELAY_3_DICT')
        queue.enqueue(update_device_data, current_app.config, db_path, 'RELAY_4_DICT')
        queue.enqueue(update_device_data, current_app.config, db_path, 'SENSOR_DHT22_1_DICT')
        queue.enqueue(update_device_data, current_app.config, db_path, 'SENSOR_DS18B20_1_DICT')

        # create task for ventilation
        # schedule task to every N minutes ventilation
        next_run_time = calculate_next_loop_time(current_app.config["EXPERIMENT"]["ventilation"]["measure_cycle_time"])
        print(next_run_time)
        queue.enqueue_at(next_run_time, ventilation_loop,current_app.config)

        # # create redis queue workers for that work
        # workers = []
        # # creating one scheduled worker (must be created before regular workers somehow)
        # worker = rq.Worker(queues=['default'], connection=red)
        # workers.append(worker)
        # worker.work(with_scheduler=True)
        #
        # for i in range(8):
        #     wi = rq.Worker(['default'], connection=red)
        #     workers.append(wi)
        #     wi.work()


@click.command('start-worker')
def start_worker():
    """
    start one regular worker and block this process
    :return:
    """
    red = redis.Redis(host='localhost', port=6379)
    queue = rq.Queue('default', connection=red)
    workers = rq.Worker.count(connection=red)
    print(f"We have already {workers} workers in {queue.name} queue")
    wi = rq.Worker(['default'], connection=red)
    wi.work()


@click.command('start-scheduler')
def start_scheduler():
    """
    start one regular worker and block this process
    :return:
    """
    red = redis.Redis(host='localhost', port=6379)
    queue = rq.Queue('default', connection=red)
    workers = rq.Worker.count(connection=red)
    print(f"We have already {workers} workers in {queue.name} queue")
    wi = rq.Worker(['default'], connection=red)
    wi.work(with_scheduler=True)


@click.command('clear-queue')
def clear_queue():
    red = redis.Redis(host='localhost', port=6379)
    queue = rq.Queue('default', connection=red)
    # Empty the queue
    queue.empty()

    # Clear Failed Jobs
    failed_registry = FailedJobRegistry(queue=queue, connection=red)
    for job_id in failed_registry.get_job_ids():
        failed_registry.remove(job_id, delete_job=True)

    # Clear Scheduled Jobs
    scheduled_registry = ScheduledJobRegistry(queue=queue, connection=red)
    for job_id in scheduled_registry.get_job_ids():
        scheduled_registry.remove(job_id, delete_job=True)


@click.command('kill-all-workers')
def kill_all_workers():
    red = redis.Redis(host='localhost', port=6379)
    queue = rq.Queue('default', connection=red)
    workers = rq.Worker.all(queue=queue)

    for worker in workers:
        print(worker.name, worker.total_working_time, worker.get_state())
        send_kill_horse_command(red, worker.name)
        send_shutdown_command(red, worker.name)



def init_tasks(app):
    app.cli.add_command(start_tasks_command)
    app.cli.add_command(start_worker)
    app.cli.add_command(start_scheduler)
    app.cli.add_command(kill_all_workers)
    app.cli.add_command(clear_queue)