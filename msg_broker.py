from redis import Redis
from rq import Queue

class Rds:
    def __init__(self,name) -> None:
        self.redis_conn = Redis(host="localhost" , port=6379)
        self.queue = Queue(name , connection=self.redis_conn)