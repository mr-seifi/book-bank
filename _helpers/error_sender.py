from _helpers.telegram_service import InternalService
from cryptor.settings import TELEGRAM_MESSAGES


def send_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            update = len(args) == 3 and args[1] or args[0]
            context = len(args) == 3 and args[2] or args[1]

            InternalService.send_error(context=context, error=ex)
            if query := update.callback_query:
                query.edit_message_text(
                    TELEGRAM_MESSAGES['user_error']
                )
            elif message := update.message:
                message.reply_text(
                    TELEGRAM_MESSAGES['user_error']
                )
    return wrapper
