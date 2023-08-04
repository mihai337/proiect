from redis import Redis
from rq import Queue

class Rds:
    redis_conn = Redis(host="localhost" , port=6379)
    queue = Queue("mod_queue" , connection=redis_conn)