import django
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (CallbackContext, Updater, Dispatcher, CommandHandler, ConversationHandler,
                          CallbackQueryHandler, MessageHandler, Filters)
from _helpers.telegram_service import InternalService
from secret import TELEGRAM_BOT_TOKEN
from django.conf import settings
from store.tasks.libgen_task import download_book
from store.models import Book


class Main:

    @staticmethod
    def start(update: Update, context: CallbackContext):
        message = update.message
        user_id = message.from_user.id

        filename, content = download_book(Book.objects.get(pk=3))
        InternalService.send_info(context=context, info=filename)

    @staticmethod
    def blind_date(update: Update, context: CallbackContext):
        message = update.message
        user_id = message.from_user.id

    @classmethod
    def menu(cls, update: Update, context: CallbackContext):
        message = update.message
        user_id = message.from_user.id


def main():
    updater = Updater(token=TELEGRAM_BOT_TOKEN,
                      use_context=True)

    # Get the dispatcher to register handlers
    dispatcher: Dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', Main.start)
    menu_handler = ConversationHandler(
        entry_points=[CommandHandler('menu', Main.menu)],
        states={
            settings.STATES['menu']: [

            ],
        },
        fallbacks=[CommandHandler('menu', Main.menu)]
    )

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(menu_handler)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully
    updater.idle()


if __name__ == '__main__':
    django.setup()

    main()
