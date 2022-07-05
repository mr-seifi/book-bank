import django
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle,
                      InputTextMessageContent)
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          InlineQueryHandler, Application)
from telegram.constants import ParseMode

from _helpers.telegram_service import InternalService
from secret import TELEGRAM_BOT_TOKEN
from django.conf import settings
import asyncio

django.setup()
from store.models import Book
from provider.tasks.download_task import download_book
from provider.services import RedirectService
from store.services import AccountCacheService


class Main:

    @staticmethod
    async def start(update: Update, context: CallbackContext):
        message = update.message
        user_id = message.from_user.id

        await message.reply_photo(
            photo='main_cover.jpg',
            caption=settings.TELEGRAM_MESSAGES['start'],
            parse_mode=ParseMode.MARKDOWN,
        )

        return

    @staticmethod
    async def check_verification(message):
        user_id = message.from_user.id

        verified = InternalService.is_user_verified(user_id=user_id)

        if not verified:
            advertisers = InternalService.should_join(user_id=user_id)
            keyboard = [
                [
                    InlineKeyboardButton(text=advertiser.channel_name,
                                         url=f'https://t.me/{advertiser.channel_id}')
                ] for advertiser in advertisers
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await message.reply_text(
                settings.TELEGRAM_MESSAGES['is_not_verified'],
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )

            return False
        return True

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
        user = update.inline_query.from_user

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

        await InternalService.send_info(context=context, info=f'[{user.full_name}](tg://user?id={user.id}) is searching'
                                                              f' for {query}! \U0001F60F')
        return response

    @staticmethod
    async def download(update: Update, context: CallbackContext):
        message = update.message
        user = message.from_user
        user_id = message.from_user.id

        verified = await Main.check_verification(message=message)
        if not verified:
            return

        account_service = AccountCacheService()
        limit = account_service.get_limit(user_id=user_id)
        if limit > settings.USER_DOWNLOAD_LIMIT:
            await message.reply_text(
                settings.TELEGRAM_MESSAGES['limited_download']
            )
            return

        md5 = context.args[0]

        await message.reply_text(
            settings.TELEGRAM_MESSAGES['waiting_for_download']
        )

        book = Book.objects.get(md5=md5)

        if book.file:
            message_id = book.file
            await InternalService.send_info(context,
                                            f'[{user.full_name}](tg://user?id={user.id}) is getting {book.title}'
                                            f' from forwarding.')
            await InternalService.forward_file(context=context,
                                               file_id=message_id,
                                               to=user_id)
        elif book.filesize >= settings.DOWNLOAD_LIMIT_SIZE:
            await InternalService.send_info(context,
                                            f'[{user.full_name}](tg://user?id={user.id}) is getting {book.title}'
                                            f' from link.')
            await message.reply_text(
                settings.TELEGRAM_MESSAGES['redirect_url'].format(title=book.title[:100],
                                                                  year=book.year,
                                                                  extension=book.extension,
                                                                  authors=book.authors[:50],
                                                                  publisher=book.publisher[:50],
                                                                  description=book.description[:250],
                                                                  url=RedirectService().generate_redirect_url(book)),
                parse_mode=ParseMode.MARKDOWN
            )

        else:
            asyncio.create_task(download_book(book, context=context, user=message.from_user))

        account_service.incr_limit(user_id=user_id)


def main():
    application = Application.builder().base_url('http://0.0.0.0:8081/bot').token(TELEGRAM_BOT_TOKEN).build()

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
