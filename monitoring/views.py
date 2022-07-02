from .services.cache_service import MonitoringCacheService, MetricsCacheService
import pandas as pd
import seaborn as sns
from django.utils import timezone


class BaseView:

    def __init__(self, service):
        self.service = service

    @staticmethod
    def visualize(data_dict: dict, title: str, xlabel: str, ylabel: str, filename: str,
                  xlim: list = None, ylim: list = None):
        pd_datas = {
            key: pd.Series({timezone.datetime.strptime(usage.split('/')[0], '%H:%M:%S').time():
                                float(usage.split('/')[1]) for usage in
                            list(map(lambda x: x.decode(), value))}) for key, value in data_dict.items()
        }

        sns.set_theme()
        plots = [series.plot(label=label) for label, series in pd_datas.items()]

        fig = plots[0].get_figure()
        fig.set_title(title)

        plots[0].set_xlabel(xlabel)
        plots[0].set_ylabel(ylabel)
        if xlim:
            plots[0].set_xlim(xlim)
        if ylim:
            plots[0].set_ylim(ylim)

        plots[0].legend()
        fig.savefig(filename)

        plots[0].clear()


class HardwareView(BaseView):

    def __init__(self):
        super(HardwareView, self).__init__(MonitoringCacheService())

    def visualize_hardware(self):
        hardware_data = {
            'cpu': self.service.get_cpu(),
            'memory': self.service.get_memory()
        }

        super(HardwareView, self).visualize(data_dict=hardware_data,
                                            title='Hardware Usage',
                                            xlabel='Time',
                                            ylabel='Usage %',
                                            filename='hardware_usage.png',
                                            ylim=[0, 100])


class MetricsView(BaseView):

    def __init__(self):
        super(MetricsView, self).__init__(MetricsCacheService())

    def visualize_account_limits(self):
        account_limits = {
            'account_limits': self.service.get_account_limits()
        }

        super(MetricsView, self).visualize(data_dict=account_limits,
                                           title='Number of Account Limits',
                                           xlabel='Time',
                                           ylabel='Count',
                                           filename='account_limits.png')

    def visualize_queue(self):
        queue = {
            'queue': self.service.get_queue()
        }

        super(MetricsView, self).visualize(data_dict=queue,
                                           title='Number of books in queue',
                                           xlabel='Time',
                                           ylabel='Count',
                                           filename='queue.png')
