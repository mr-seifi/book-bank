import django
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle,
                      InputTextMessageContent)
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          InlineQueryHandler, Application)

from _helpers.telegram_service import InternalService
from secret import TELEGRAM_BOT_TOKEN
from django.conf import settings
import asyncio

django.setup()
from provider.tasks.libgen_task import send_book
from store.models import Book
from provider.tasks.download_task import download_book


class Main:

    @staticmethod
    async def start(update: Update, context: CallbackContext):
        message = update.message
        user_id = message.from_user.id
        # asyncio.run(download_books(context))

    @staticmethod
    async def blind_date(update: Update, context: CallbackContext):
        message = update.message
        user_id = message.from_user.id

    @classmethod
    async def menu(cls, update: Update, context: CallbackContext):
        message = update.message
        user_id = message.from_user.id

        keyboard = [
            [
                InlineKeyboardButton('دانلود', callback_data='DOWNLOAD')
            ]
        ]

        await message.reply_text(
            'OK CLICK',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return 1

    @staticmethod
    async def download_inline(update: Update, context: CallbackContext):
        from uuid import uuid4

        query = update.inline_query.query

        if query == "":
            return

        results = [
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=book.title,
                input_message_content=InputTextMessageContent(f'/download {book.md5}'),
                thumb_url=book.cover_url,
                description=f'{book.year}-{book.extension}-{book.filesize // 1000000}MB\n'
                            f'{book.authors}\n{book.publisher}\n{book.description}'
            ) for book in Book.objects.filter(document__exact=query).exclude(title__exact='').order_by('document')[:25]
        ]
        response = await update.inline_query.answer(results)
        return response

    @staticmethod
    async def download(update: Update, context: CallbackContext):
        message = update.message
        user_id = message.from_user.id

        md5 = context.args[0]

        await message.reply_text(
            settings.TELEGRAM_MESSAGES['waiting_for_download']
        )

        book = Book.objects.get(md5=md5)

        if book.file:
            message_id = book.file
            await InternalService.forward_file(context=context,
                                               file_id=message_id,
                                               to=user_id)
        else:
            asyncio.create_task(download_book(book, context=context, user_id=user_id))

        # asyncio.create_task(send_book(md5, context, user_id))


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).base_url('https://0.0.0.0:8081').build()

    start_handler = CommandHandler('start', Main.start)
    menu_handler = ConversationHandler(
        entry_points=[CommandHandler('menu', Main.menu)],
        states={
            1: [

            ],
        },
        fallbacks=[CommandHandler('menu', Main.menu)]
    )
    download_handler = CommandHandler('download', Main.download)

    application.add_handler(start_handler)
    application.add_handler(menu_handler)
    application.add_handler(download_handler)
    application.add_handler(InlineQueryHandler(Main.download_inline))

    # Start the Bot
    application.run_polling()


if __name__ == '__main__':
    django.setup()

    main()
