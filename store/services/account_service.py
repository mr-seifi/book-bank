from _helpers.cache_service import CacheService
import os


class AccountCacheService(CacheService):
    PREFIX = 'ACCOUNT'
    REDIS_KEYS = {
        'limit': f'{PREFIX}'':LIMIT_{user_id}'
    }
    EX = 60 * 60

    def incr_limit(self, user_id):
        self.incr_from_redis(self.REDIS_KEYS['limit'].format(user_id=user_id))

    def get_limit(self, user_id):
        return self.get_from_redis(self.REDIS_KEYS['limit'].format(user_id=user_id))

    @staticmethod
    def delete_limits():
        os.system('redis-cli KEYS "ACCOUNT:LIMIT_*" | xargs redis-cli DEL')
