import time
from flaskr.tasks.rq_tasks import short_task, short_periodical_task, long_periodical_task, count_words_at_url
import rq
import redis


def init_tasks():
    queue.enqueue(short_task, 100)
    queue.enqueue(short_task, 120)
    queue.enqueue(short_task, 150)
    queue.enqueue(short_periodical_task, 'localhost', 6379, "default", -1)


if __name__ == "__main__":
    r = redis.Redis(host='localhost', port=6379)
    queue = rq.Queue(connection=r)
    queue.enqueue(short_task, 11)
    init_tasks()

    # start two new workers and sleep forever
    w = rq.Worker(['default'], connection=r)
    w_sch = rq.Worker(['default'], connection=r)
    w_sch.work(with_scheduler=True)
    w.work()

