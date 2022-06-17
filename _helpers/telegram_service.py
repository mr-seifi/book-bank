from secret import TELEGRAM_INFO_GROUP, TELEGRAM_WARNING_GROUP, TELEGRAM_ERROR_GROUP
from telegram import ParseMode
from django.conf import settings


class InternalService:

    @staticmethod
    def _send_message(context, message, to):
        context.bot.send_message(chat_id=to,
                                 text=message,
                                 parse_mode=ParseMode.MARKDOWN)

    @classmethod
    def send_info(cls, context, info):
        cls._send_message(context=context,
                          message=settings.TELEGRAM_MESSAGES['info'].format(info=str(info)),
                          to=TELEGRAM_INFO_GROUP)

    @classmethod
    def send_warning(cls, context, warning):
        cls._send_message(context=context,
                          message=settings.TELEGRAM_MESSAGES['warning'].format(warning=str(warning)),
                          to=TELEGRAM_WARNING_GROUP)

    @classmethod
    def send_error(cls, context, error):
        cls._send_message(context=context,
                          message=settings.TELEGRAM_MESSAGES['error'].format(ex=str(error)),
                          to=TELEGRAM_ERROR_GROUP)
