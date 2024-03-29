import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from django.conf import settings
from store.models import Book
from ..services.zlib_service import ZLibService
from ..services.libgen_service import LibgenService
from _helpers.telegram_service import InternalService
from .libgen_task import _download_cover
from aiohttp import ClientSession
from store.services import QueueCacheService
import asyncio


async def download_book(book: Book, context, user):
    user_id = user.id
    zlib_service = ZLibService()
    filename = f'{LibgenService.get_book_identifier(book.__dict__)}.{book.extension}'
    queue_service = QueueCacheService()

    queue_service.incr_queue()
    if book.cover_url:
        _download_cover(requests.Session(), book)

    async with ClientSession() as session:
        try:
            await InternalService.send_info(context, f'[{user.full_name}](tg://user?id={user.id}) is getting '
                                                     f'{InternalService.markdown_escape(filename)}'
                                                     f' from ZLIB.')
            content = await zlib_service.download_book(book.md5, session)
        except Exception as ex:
            asyncio.create_task(InternalService.send_error(context, ex))
            await InternalService.send_info(context, f'[{user.full_name}](tg://user?id={user.id}) is getting '
                                                     f'{InternalService.markdown_escape(filename)}'
                                                     f' from LIBGEN!')

            if not book.download_url:
                asyncio.create_task(
                    InternalService.send_message_to_users([user_id], message=settings.TELEGRAM_MESSAGES['cannot_find'])
                )

                return

            result = await session.get(book.download_url)
            content = await result.read()

            del result

    if book.cover:
        message_id = await InternalService.send_file(context=context, file=content, filename=filename,
                                                     thumb=book.cover,
                                                     description=f'*{book.title}*\n{book.description}'[:500]
                                                                 + f'...\n\n#{book.topic}\n@BookBank_RoBot')
    else:
        message_id = await InternalService.send_file(context=context, file=content, filename=filename,
                                                     description=f'*{book.title}*\n{book.description}'[:500]
                                                                 + f'...\n\n#{book.topic}\n@BookBank_RoBot')

    del content

    book.file = message_id
    book.save()

    await InternalService.forward_file(context=context,
                                       file_id=message_id,
                                       to=user_id)
    queue_service.decr_queue()
    print('[+] Done!')
