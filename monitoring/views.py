from .services.cache_service import MonitoringCacheService
import pandas as pd
from django.utils import timezone


class HardwareView:

    def __init__(self):
        self.service = MonitoringCacheService()

    def visualize_cpu_usage(self):
        cpu_usage = pd.Series({timezone.datetime.strptime(usage.split('/')[0], '%H:%M:%S').time():
                                   float(usage.split('/')[1]) for usage in
                               list(map(lambda x: x.decode(), self.service.get_cpu()))})
        plot = cpu_usage.plot(colormap='jet', title='Memory Usage')

        fig = plot.get_figure()
        plot.set_xlabel('Time')
        plot.set_ylabel('Usage')

        fig.savefig("cpu_usage.png")

    def visualize_memory_usage(self):
        memory_usage = pd.Series({timezone.datetime.strptime(usage.split('/')[0], '%H:%M:%S').time():
                                      float(usage.split('/')[1]) for usage in
                                  list(map(lambda x: x.decode(), self.service.get_memory()))})
        plot = memory_usage.plot(colormap='jet', title='Memory Usage')

        fig = plot.get_figure()
        plot.set_xlabel('Time')
        plot.set_ylabel('Usage')

        fig.savefig("memory_usage.png")
