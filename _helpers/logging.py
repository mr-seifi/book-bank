import asyncio
from .telegram_service import InternalService


class Logger:

    @staticmethod
    def info(message):
        asyncio.run(
            InternalService.send_info(context=None, info=message)
        )

    @staticmethod
    def warning(message):
        asyncio.run(
            InternalService.send_warning(context=None, warning=message)
        )

    @staticmethod
    def error(message):
        asyncio.run(
            InternalService.send_error(context=None, error=message)
        )


logger = Logger()
