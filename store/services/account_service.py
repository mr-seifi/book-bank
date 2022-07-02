from _helpers.cache_service import CacheService
import os
from django.conf import settings


class AccountCacheService(CacheService):
    PREFIX = 'ACCOUNT'
    REDIS_KEYS = {
        'limit': f'{PREFIX}'':LIMIT_{user_id}'
    }
    EX = 60 * 60

    def incr_limit(self, user_id):
        self.incr_from_redis(self.REDIS_KEYS['limit'].format(user_id=user_id))

    def get_limit(self, user_id):
        return int(self.get_from_redis(self.REDIS_KEYS['limit'].format(user_id=user_id)).decode())

    def get_limited_keys(self):
        return self.get_keys(pattern=f'{self.PREFIX}:LIMIT_*')

    def delete_limits(self):
        os.system(f'redis-cli KEYS "{self.PREFIX}:LIMIT_*" | xargs redis-cli DEL')


class AccountService:

    @staticmethod
    def limited_accounts_count():
        service = AccountCacheService()

        limited_keys = service.get_limited_keys()
        return sum([1 for key in limited_keys if service.get_limit(user_id=key.split('_')[1]) >=
                    settings.USER_DOWNLOAD_LIMIT])


class QueueCacheService(CacheService):
    PREFIX = 'QUEUE'
    REDIS_KEYS = {
        'count': f'{PREFIX}'':COUNT'
    }
    EX = 60 * 60 * 24

    def incr_queue(self):
        return self.incr_from_redis(self.REDIS_KEYS['count'])

    def decr_queue(self):
        return self.decr_from_redis(self.REDIS_KEYS['count'])

    def get_queue(self):
        return int(self.get_from_redis(self.REDIS_KEYS['count']).decode())


class QueueService:

    @staticmethod
    def get_queue_count():
        service = QueueCacheService()
        return service.get_queue()
