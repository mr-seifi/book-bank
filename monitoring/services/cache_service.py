from _helpers.cache_service import CacheService
from django.utils import timezone
from .hardware_service import HardwareService
from store.services import AccountService, QueueService


class MonitoringCacheService(CacheService):
    PREFIX = 'MONITORING'
    REDIS_KEYS = {
        'cpu': f'{PREFIX}'':cpu',
        'memory': f'{PREFIX}'':memory'
    }

    def cache_cpu(self):
        return self.lpush(self.REDIS_KEYS['cpu'],
                          f"{timezone.now().strftime('%H:%M:%S')}/{HardwareService.cpu_usage()}")

    def get_cpu(self):
        return self.lrange(key=self.REDIS_KEYS['cpu'])

    def delete_cpu(self):
        return self.delete(self.REDIS_KEYS['cpu'])

    def cache_memory(self):
        return self.lpush(self.REDIS_KEYS['memory'],
                          f"{timezone.now().strftime('%H:%M:%S')}/{HardwareService.memory_usage()}")

    def get_memory(self):
        return self.lrange(key=self.REDIS_KEYS['memory'])

    def delete_memory(self):
        return self.delete(self.REDIS_KEYS['memory'])


class MetricsCacheService(CacheService):
    PREFIX = 'METRICS'
    REDIS_KEYS = {
        'account_limits': f'{PREFIX}'':ACCOUNT_LIMITS',
        'queue': f'{PREFIX}'':QUEUE'
    }

    def cache_account_limits(self):
        return self.lpush(self.REDIS_KEYS['account_limits'],
                          f"{timezone.now().strftime('%H:%M:%S')}/{AccountService.limited_accounts_count()}")

    def get_account_limits(self):
        return self.lrange(key=self.REDIS_KEYS['account_limits'])

    def delete_account_limits(self):
        return self.delete(self.REDIS_KEYS['account_limits'])

    def cache_queue(self):
        return self.lpush(self.REDIS_KEYS['queue'],
                          f"{timezone.now().strftime('%H:%M:%S')}/{QueueService.get_queue_count()}")

    def get_queue(self):
        return self.lrange(key=self.REDIS_KEYS['queue'])

    def delete_queue(self):
        return self.delete(self.REDIS_KEYS['queue'])
