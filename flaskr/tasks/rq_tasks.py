import redis
import rq
import time
from datetime import datetime, timedelta

import requests
device_path = "/home/bigfoot/PycharmProjects/clay_golem/flaskr/tasks/device1.txt"

def count_words_at_url(url):
    resp = requests.get(url)
    return len(resp.text.split())


# user-defined tasks to work with low-level drivers
def short_task(data):
    # short task - do something with stub device and done
    red = redis.Redis(host='localhost', port=6379, decode_responses=True)
    # get device lock
    # or sleep until get it
    lock_acquired = 0
    while not lock_acquired:
        lock_acquired = red.set("lock:device1", "test", ex=10, nx=True)
        time.sleep(0.1)

    # when lock acquired
    with open(device_path, 'a') as file1:
        date_ = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        file1.write(date_ + " : short task started! : " + str(data)+ "\n")
        time.sleep(1)
        date_ = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        file1.write(date_ + " : short task ended! : " + str(data) + "\n")

    # free lock
    lock_deleted = red.delete("lock:device1", "test")


def short_periodical_task(rhost, rport, qname, i):
    # periodical task, works everytime but mostly sleeps, waiting for signal from redis or time
    # it scheduling itself to next run
    red = redis.Redis(host=rhost, port=rport, decode_responses=True)
    queue_ = rq.Queue(connection=red, name=qname)
    # get device lock
    # or sleep until get it
    lock_acquired = 0
    while not lock_acquired:
        lock_acquired = red.set("lock:device1", "test", ex=10, nx=True)
        time.sleep(0.1)

    # when lock acquired
    with open(device_path, 'a') as file1:
        date_ = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        file1.write(date_ + " : short periodical task started! : " + str(i)+ "\n")
        time.sleep(1)
        date_ = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        file1.write(date_ + " : short periodical task ended! : " + str(i)+ "\n")

    # free lock
    lock_deleted = red.delete("lock:device1", "test")

    # schedule itself again
    queue_.enqueue_in(timedelta(seconds=10), short_periodical_task, rhost, rport, qname, i-1)


def long_periodical_task():
    # it needs to acquire lock several times
    pass