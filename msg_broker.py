from redis import Redis
from rq import Queue

class Rds:
    def __init__(self,name) -> None:
        self.redis_conn = Redis(host="redis-10048.c3.eu-west-1-2.ec2.redns.redis-cloud.com",
                                port=10048,
                                password="qJMaxwRfl8fnlKowyvj6g3eQBWpBh3x1")
        self.queue = Queue(name , connection=self.redis_conn)