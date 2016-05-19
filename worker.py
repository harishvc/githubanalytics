#https://devcenter.heroku.com/articles/python-rq

import os
import redis
from rq import Worker, Queue, Connection

from Neo4jQueries import FindSimilarRepositories   

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://127.0.0.1:6379')

#print("Redis URL ====", redis_url)

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
