import os

import redis

r = redis.Redis(
    host=os.environ.get("REDIS_HOST"),
    port=int(os.environ.get("REDIS_PORT")),
    db=int(os.environ.get("REDIS_DB")),
)
