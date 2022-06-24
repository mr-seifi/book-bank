from .services.cache_service import MonitoringCacheService
import pandas as pd
from django.utils import timezone


class HardwareView:

    def __init__(self):
        self.service = MonitoringCacheService()

    def visualize_cpu_usage(self):
        cpu_usage = {timezone.datetime.strptime(usage.split('/')[0], '%H:%M:%S').time():
                         float(usage.split('/')[1]) for usage in
                     list(map(lambda x: x.decode(), self.service.get_cpu()))}
        print(cpu_usage)
        cpu_usage_df = pd.Series(cpu_usage)
        plot = cpu_usage_df.plot()

        fig = plot.get_figure()
        fig.savefig("cpu_usage.png")
