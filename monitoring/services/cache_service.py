from _helpers.cache_service import CacheService
from django.utils import timezone
from .hardware_service import HardwareService


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
