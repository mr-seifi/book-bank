from .services.cache_service import MonitoringCacheService
import pandas as pd
from django.utils import timezone
import seaborn as sns


class HardwareView:

    def __init__(self):
        self.service = MonitoringCacheService()

    def visualize(self):
        cpu_usage = pd.Series({timezone.datetime.strptime(usage.split('/')[0], '%H:%M:%S').time():
                                   float(usage.split('/')[1]) for usage in
                               list(map(lambda x: x.decode(), self.service.get_cpu()))})
        memory_usage = pd.Series({timezone.datetime.strptime(usage.split('/')[0], '%H:%M:%S').time():
                                      float(usage.split('/')[1]) for usage in
                                  list(map(lambda x: x.decode(), self.service.get_memory()))})

        sns.set_theme()
        plot = cpu_usage.plot(label='cpu')
        memory_usage.plot(title='Hardware Usage', label='memory')

        fig = plot.get_figure()
        plot.set_xlabel('Time')
        plot.set_ylabel('Usage %')
        plot.set_ylim([0, 100])

        plot.legend()
        fig.savefig("hardware_usage.png")

        plot.clear()
