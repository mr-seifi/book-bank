import asyncio
import aiohttp
import requests
from django.core.files.base import ContentFile
from _helpers.telegram_service import InternalService
from store.models import Book
from store.services.libgen_service import LibgenService
from concurrent.futures import ThreadPoolExecutor
from multiprocessing.pool import Pool
from _helpers import batch
from django.conf import settings

books = []


def _add_book(book: dict):
    global books

    try:
        if Book.objects.filter(libgen_id=book['id']):
            print(f'[-] Passed: {book["id"]}')
            return

        book = Book(libgen_id=book['id'],
                    title=book['title'],
                    series=book['series'],
                    year=book['year'],
                    authors=book['authors'],
                    edition=book['edition'],
                    publisher=book['publisher'],
                    pages=book['pages'] or None,
                    language=book['language'],
                    filesize=book['filesize'],
                    extension=book['extension'],
                    topic=book['topic'] or 'Other',
                    identifier=book['identifier'],
                    md5=book['md5'],
                    description=book.get('description', ''),
                    download_url=book.get('link', ''),
                    cover_url=LibgenService.get_cover_url(book), )
        books.append(book)

    except Exception as ex:
        print(f'[-] {ex}, data: {book}')


def add_books_to_database_online(limit=5000, offset=0):
    libgen_service = LibgenService()

    for batch in libgen_service.read_book_from_mysql(limit=limit, offset=offset):
        print('[+] Assign process started!')
        libgen_service.assign_more_information_online(batch)
        print('[+] Assigned successfully!')

        with Pool() as pool:
            pool.starmap(_add_book, [(book,) for book in batch])


def add_books_to_database(limit=30000, offset=0):
    libgen_service = LibgenService()
    global books

    for batch in libgen_service.read_book_from_mysql(limit=limit, offset=offset):
        with ThreadPoolExecutor() as executor:
            executor.map(_add_book, batch)
        try:
            Book.objects.bulk_create(books)
            print('[+] batch created!')
        except:
            pass
        books.clear()


downloaded = 0
all_covers = 0

to_download_covers = []


def _download_cover(session: requests.Session, book: Book, bulk=False):
    global downloaded, all_covers, to_download_covers

    name = f'{LibgenService.get_book_identifier(book.__dict__)}.{book.cover_url.split(".")[-1]}'
    content = ContentFile(session.get(book.cover_url).content, name=name)
    if bulk:
        book.cover.save(name=name, content=content, save=False)
        to_download_covers.append(book)
    else:
        book.cover.save(name=name, content=content, save=True)
    print(book.cover)
    downloaded += 1
    print(f'\rProcess: {100 * downloaded / all_covers:.2f}%', end='')


def download_covers():
    global all_covers
    n = 200
    all_covers = n
    book_list = Book.objects.filter(cover__exact='')[:n]

    if not book_list:
        return

    with ThreadPoolExecutor() as executor:
        with requests.Session() as session:
            executor.map(_download_cover, [session] * n, book_list, [True] * n)
            executor.shutdown(wait=True)
        Book.objects.bulk_update(book_list, fields=['cover'])
        to_download_covers.clear()


to_download_books = []


async def _download_book(book: Book, session, context, bulk=False):
    global to_download_books

    print(f'[+] Download {book.title} started!')
    result = await session.get(book.download_url)
    content = await result.read()
    filename = f'{LibgenService.get_book_identifier(book.__dict__)}.{book.extension}'
    if not book.cover or (book.cover and book.updated < settings.RELEASE_DATE):
        cover_name, cover = await LibgenService.download_cover(book, session)
        cover = ContentFile(cover, name=cover_name)
        book.cover.save(name=cover_name, content=cover, save=False)
        book.save()

    message_id = InternalService.send_file(context=context, file=content, filename=filename,
                                           thumb=book.cover,
                                           description=f'*{book.title}*\n{book.description}'[:500]
                                                       + f'...\n\n#{book.topic}\n@BookBank_RoBot')
    book.file = message_id

    if bulk:
        to_download_books.append(book)
    else:
        book.save()

    print(f'[+] Download ended!')

    return message_id


async def download_books(context):
    global to_download_books

    book_list = Book.objects.filter(file__isnull=True)

    for book_batch in batch(book_list, n=3):
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *[
                    _download_book(book,
                                   session,
                                   context,
                                   True) for book in book_batch
                ]
            )
        Book.objects.bulk_update(to_download_books, fields=['file'])
        to_download_books.clear()


async def send_book(md5: str, context, user_id):
    book = Book.objects.get(md5=md5)

    if book.file:
        message_id = book.file
    else:
        async with aiohttp.ClientSession() as session:
            message_id = await _download_book(book, session, context)

    await InternalService.forward_file(context=context,
                                       file_id=message_id,
                                       to=user_id)
