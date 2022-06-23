from .redis_client import get_redis_client, Redis
from .singleton import singleton


@singleton
class CacheService:

    def __init__(self):
        self.client: Redis = get_redis_client()

    def cache_on_redis(self, key: str, value: str, ttl: int):
        self.client.set(name=key, value=value, ex=ttl)

    def get_from_redis(self, key: str):
        return self.client.get(name=key) or b'0'

    def incr_from_redis(self, key: str, ttl=0):
        if ttl:
            self.cache_on_redis(key, self.get_from_redis(key) or 0, ttl)
        return self.client.incr(name=key)
