import re
from bs4 import BeautifulSoup
import requests
from mysql.connector import connect
from concurrent.futures import ThreadPoolExecutor
import logging
from django.utils.text import slugify


class LibgenService:
    _instance = None
    assigned_cnt = 0
    BASE_DOWNLOAD_FILE = '62.182.86.140'
    BASE_DOWNLOAD_COVER = 'library.lol'

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance') or not getattr(cls, '_instance'):
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'conn') or not getattr(self, 'conn'):
            from secret import MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_HOST
            self.conn = connect(user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB, host=MYSQL_HOST)

    def read_book_from_mysql(self, limit=100000, offset=0):
        cursor = self.conn.cursor()
        select_query = 'SELECT * FROM updated u ' \
                       'LEFT JOIN topics t ON u.topic = t.topic_id ' \
                       'WHERE u.Language = "English" AND (t.lang = "en" OR t.lang IS NULL)' \
                       ' LIMIT {limit} OFFSET {offset}'
        cursor.execute(select_query.format(limit=limit, offset=offset))
        data = cursor.fetchall()

        while data:
            offset += limit
            yield self.assign_more_information(book_batch=LibgenService._libgen_record_to_dict(data=data))
            cursor.execute(select_query.format(limit=limit, offset=offset))
            data = cursor.fetchall()

    def assign_more_information(self, book_batch: list):
        book_batch = self._add_description(book_batch=book_batch)
        for book in book_batch:
            book['link'] = self.get_download_url(book)

        return book_batch

    def _add_description(self, book_batch: list) -> list:
        md5_to_book_dict = {book['md5'].lower(): book for book in book_batch}

        cursor = self.conn.cursor()
        select_query = 'SELECT md5, descr FROM description ' \
                       'WHERE md5 IN ({})'.format(', '.join(f'"{word}"' for word in list(md5_to_book_dict)))
        cursor.execute(select_query)

        for md5, descr in cursor:
            md5 = md5.lower()
            descr = descr.decode() if isinstance(descr, bytes) else descr

            try:
                md5_to_book_dict[md5]['description'] = descr
            except Exception as ex:
                logging.exception(ex)
                print(f'[-] Skipped {ex}')

        return [md5_to_book_dict[md5] for md5 in md5_to_book_dict]

    @classmethod
    def get_cover_url(cls, book: dict):
        return f"http://{cls.BASE_DOWNLOAD_COVER}/covers/{book.get('cover_url', '')}" if book.get('cover_url') else ''

    @classmethod
    def get_download_url(cls, book: dict) -> str:
        try:
            url = f"http://{cls.BASE_DOWNLOAD_FILE}/main/" \
                  f"{book.get('cover_url', '').replace('-d', '').replace('-g', '').split('.')[-2]}/" \
                  f"{cls.get_book_identifier(book)}" \
                  f".{book['extension']}" \
                if book.get('cover_url') and book.get('extension') and 'cover' not in book.get('cover_url') \
                else ''

            return url
        except Exception as ex:
            logging.exception(ex)
            return ''

    @classmethod
    def get_book_identifier(cls, book: dict) -> str:
        return slugify('{} {} {} {}'.format(book['title'], book['publisher'], book['year'], 'pdfbaz'))

    @staticmethod
    def split_authors(authors: str) -> list:
        return [author.strip() for author in authors.split(',') if author]

    @staticmethod
    def assign_more_information_online(book_list: list):
        with ThreadPoolExecutor() as executor:
            with requests.Session() as session:
                executor.map(LibgenService._assign_more_information_online, book_list, [session] * len(book_list))
                executor.shutdown()

    @staticmethod
    def _assign_more_information_online(book: dict, session: requests.Session):
        description = LibgenService._get_description_online(book=book,
                                                            session=session)
        link = LibgenService._get_book_link_online(book=book,
                                                   session=session)
        if description:
            book['description'] = description
        if link:
            book['link'] = link

        LibgenService.assigned_cnt += 1
        print(f'\r[+] Assigning progress: {LibgenService.assigned_cnt}', end='')
        return book

    @staticmethod
    def _get_description_online(book: dict, session: requests.Session, retries=5, cnt=0):
        base_url = 'http://library.lol/main/'

        if not book.get("md5"):
            return

        url = f'{base_url}{book.get("md5")}'
        response = session.get(url)

        if response.status_code != 200:
            if cnt >= retries:
                return

            return LibgenService._get_description_online(book=book,
                                                         session=session,
                                                         cnt=cnt + 1)

        soup = BeautifulSoup(response.text, 'html.parser')
        if result := re.findall(r'<div>Description:<br\/>(.+)<\/div>', str(soup)):
            return result[0]

    @staticmethod
    def _get_book_link_online(book: dict, session: requests.Session, retries=5, cnt=0):
        base_url = 'http://library.lol/main/'

        if not book.get("md5"):
            return

        url = f'{base_url}{book.get("md5")}'
        response = session.get(url)

        if response.status_code != 200:
            if cnt >= retries:
                return

            return LibgenService._get_description_online(book=book,
                                                         session=session,
                                                         cnt=cnt + 1)

        soup = BeautifulSoup(response.text, 'html.parser')
        if result := re.findall(r'<a href="(.+)">GET<\/a>', str(soup)):
            return result[0]

    @staticmethod
    def _libgen_record_to_dict(data):
        return list(map(lambda book: {'id': book[0],
                                      'title': book[1],
                                      'series': book[3],
                                      'authors': book[5],
                                      'year': book[6] or None,
                                      'edition': book[7],
                                      'publisher': book[8],
                                      'pages': book[10] if '-' not in str(book[10]) else str(book[10]).split('-')[-1],
                                      'pages_in_file': book[11],
                                      'language': book[12],
                                      'identifier': book[16],
                                      'issn': book[17],
                                      'asin': book[18],
                                      'udc': book[19],
                                      'lbc': book[20],
                                      'ddc': book[21],
                                      'lcc': book[22],
                                      'doi': book[23],
                                      'openlibrary_id': book[24],
                                      'filesize': book[35],
                                      'extension': book[36],
                                      'md5': book[37],
                                      'cover_url': book[44],
                                      'topic': book[48]}, data))

    @staticmethod
    async def download_cover(book, session):
        name = f'{LibgenService.get_book_identifier(book.__dict__)}.{book.cover_url.split(".")[-1]}'
        response = await session.get(book.cover_url)

        return name, response
