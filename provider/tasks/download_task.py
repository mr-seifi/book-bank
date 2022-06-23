import requests
from store.models import Book
from ..services.zlib_service import ZLibService
from ..services.libgen_service import LibgenService
from _helpers.telegram_service import InternalService
from .libgen_task import _download_cover


def download_book(book: Book, context, user_id):
    zlib_service = ZLibService()
    filename = f'{LibgenService.get_book_identifier(book.__dict__)}.{book.extension}'

    if not book.cover:
        _download_cover(requests.Session(), book)

    with requests.Session() as session:
        try:
            content = zlib_service.download_book(book.md5, session)
        except Exception as ex:
            print(ex)
            result = session.get(book.download_url)
            content = result.content

    message_id = InternalService.send_file(context=context, file=content, filename=filename,
                                           thumb=book.cover,
                                           description=f'*{book.title}*\n{book.description}'[:500]
                                                       + f'...\n\n#{book.topic}\n@BookBank_RoBot')

    InternalService.forward_file(context=context,
                                 file_id=message_id,
                                 to=user_id)

    book.file = message_id
    book.save()