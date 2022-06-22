from secret import TELEGRAM_INFO_GROUP, TELEGRAM_WARNING_GROUP, TELEGRAM_ERROR_GROUP, TELEGRAM_FILES_CHANNEL
from telegram import ParseMode
from django.conf import settings


class InternalService:

    @staticmethod
    def _send_message(context, message, to):
        result = context.bot.send_message(chat_id=to,
                                          text=message,
                                          parse_mode=ParseMode.MARKDOWN)
        return result.message_id

    @staticmethod
    def _send_file(context, file, filename, thumb, caption):
        result = context.bot.send_document(chat_id=TELEGRAM_FILES_CHANNEL,
                                           document=file,
                                           filename=filename,
                                           thumb=thumb,
                                           caption=caption)
        return result.message_id

    @classmethod
    def send_info(cls, context, info):
        return cls._send_message(context=context,
                                 message=settings.TELEGRAM_MESSAGES['info'].format(info=str(info)),
                                 to=TELEGRAM_INFO_GROUP)

    @classmethod
    def send_warning(cls, context, warning):
        return cls._send_message(context=context,
                                 message=settings.TELEGRAM_MESSAGES['warning'].format(warning=str(warning)),
                                 to=TELEGRAM_WARNING_GROUP)

    @classmethod
    def send_error(cls, context, error):
        return cls._send_message(context=context,
                                 message=settings.TELEGRAM_MESSAGES['error'].format(ex=str(error)),
                                 to=TELEGRAM_ERROR_GROUP)

    @classmethod
    def send_file(cls, context, file, filename, thumb, description):
        response = cls._send_file(context=context,
                                  file=file,
                                  filename=filename,
                                  thumb=thumb,
                                  caption=description)
        return response

    @staticmethod
    def forward_file(context, file_id, to):
        context.bot.forward_message(chat_id=to,
                                    from_chat_id=TELEGRAM_FILES_CHANNEL,
                                    message_id=file_id)
