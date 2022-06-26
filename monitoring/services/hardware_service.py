import psutil


class HardwareService:

    @staticmethod
    def cpu_usage():
        return psutil.cpu_percent()

    @staticmethod
    def memory_usage():
        return psutil.virtual_memory()[2]
