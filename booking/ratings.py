import redis
import os
from django.conf import settings

if settings.DEBUG:
    r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB)
else:
    r = redis.StrictRedis.from_url(os.environ.get("REDIS_URL"))