import uuid

import django
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle,
                      InputTextMessageContent)
from telegram.ext import (CallbackContext, Updater, Dispatcher, CommandHandler, ConversationHandler,
                          CallbackQueryHandler, MessageHandler, Filters, InlineQueryHandler)
from _helpers.telegram_service import InternalService
from secret import TELEGRAM_BOT_TOKEN
from django.conf import settings
import asyncio
from aiohttp import ClientSession

django.setup()
from store.tasks.libgen_task import download_books
from store.models import Book


class Main:

    @staticmethod
    def start(update: Update, context: CallbackContext):
        message = update.message
        user_id = message.from_user.id
        asyncio.run(download_books(context))

    @staticmethod
    def blind_date(update: Update, context: CallbackContext):
        message = update.message
        user_id = message.from_user.id

    @classmethod
    def menu(cls, update: Update, context: CallbackContext):
        message = update.message
        user_id = message.from_user.id

        keyboard = [
            [
                InlineKeyboardButton('دانلود', callback_data='DOWNLOAD')
            ]
        ]

        message.reply_text(
            'OK CLICK',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return 1

    @staticmethod
    def download_inline(update: Update, context: CallbackContext):
        from uuid import uuid4
        from telegram import ParseMode
        from html import escape
        query = update.inline_query.query

        if query == "":
            return

        results = [
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=book.title,
                input_message_content=InputTextMessageContent(query.upper()),
                thumb_url=book.cover.path,
                description=book.description
            ) for book in Book.objects.filter(document__exact=query)[:10]
        ]

        return update.inline_query.answer(results)


def main():
    updater = Updater(token=TELEGRAM_BOT_TOKEN,
                      use_context=True)

    # Get the dispatcher to register handlers
    dispatcher: Dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', Main.start)
    menu_handler = ConversationHandler(
        entry_points=[CommandHandler('menu', Main.menu)],
        states={
            1: [

            ],
        },
        fallbacks=[CommandHandler('menu', Main.menu)]
    )

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(menu_handler)
    dispatcher.add_handler(InlineQueryHandler(Main.download_inline))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully
    updater.idle()


if __name__ == '__main__':
    django.setup()

    main()
