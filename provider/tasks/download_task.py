import requests
from store.models import Book
from ..services.zlib_service import ZLibService
from ..services.libgen_service import LibgenService
from _helpers.telegram_service import InternalService
from .libgen_task import _download_cover
from aiohttp import ClientSession


async def download_book(book: Book, context, user_id):
    zlib_service = ZLibService()
    filename = f'{LibgenService.get_book_identifier(book.__dict__)}.{book.extension}'

    if not book.cover:
        _download_cover(requests.Session(), book)

    async with ClientSession() as session:
        try:
            content = await zlib_service.download_book(book.md5, session)
            await InternalService.send_info(context, f'Getting {filename} from ZLIB.')
        except Exception as ex:
            print(ex)
            await InternalService.send_info(context, f'Getting {filename} from LIBGEN!')
            result = await session.get(book.download_url)
            content = await result.read()

    message_id = await InternalService.send_file(context=context, file=content, filename=filename,
                                                 thumb=book.cover,
                                                 description=f'*{book.title}*\n{book.description}'[:500]
                                                             + f'...\n\n#{book.topic}\n@BookBank_RoBot')
    print(message_id)

    book.file = message_id
    book.save()

    response = await InternalService.forward_file(context=context,
                                                  file_id=message_id,
                                                  to=user_id)

    print(response)
