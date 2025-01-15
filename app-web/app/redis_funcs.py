import logging
import json
import redis

from app import settings

logger = logging.getLogger(__name__)

redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)


async def set_key(key, value, expiration_time=3600):
    redis_client.setex(key, expiration_time, value)
    return True


async def get_key(key):
    value = redis_client.get(key)
    if value is None:
        return None
    return value


def store_dict_in_redis(key, dictionary, expiration_time=3600):
    try:
        serialized_data = json.dumps(dictionary)
        redis_client.setex(key, expiration_time, serialized_data)
    except Exception as error:
        return False, str(error)
    return True, "Stored"


def get_dict_from_redis(key):
    serialized_data = redis_client.get(key)
    if serialized_data:
        return json.loads(serialized_data)
    return None


def delete_redis_key(key):
    try:
        redis_client.delete(key)
    except Exception as error:
        return False, str(error)
    return True, "Deleted key %s" % key
