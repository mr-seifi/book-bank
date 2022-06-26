from .redis_client import get_redis_client, Redis
from .singleton import singleton


class CacheService:

    def __init__(self):
        self.client: Redis = get_redis_client()

    def cache_on_redis(self, key: str, value: str, ttl: int = 0):
        if ttl:
            self.client.set(name=key, value=value, ex=ttl)
        else:
            self.client.set(name=key, value=value)

    def get_from_redis(self, key: str):
        return self.client.get(name=key) or b'0'

    def incr_from_redis(self, key: str, ttl=0):
        if ttl:
            self.cache_on_redis(key, self.get_from_redis(key) or 0, ttl)
        return self.client.incr(name=key)

    def lpush(self, key, *values):
        return self.client.lpush(key, *values)

    def rpush(self, key, *values):
        return self.client.rpush(key, *values)

    def lrange(self, key, l=0, r=2880):
        return self.client.lrange(name=key, start=l, end=r)

    def delete(self, *keys):
        return self.client.delete(*keys)
