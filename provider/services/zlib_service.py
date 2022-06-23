from _helpers.cache_service import CacheService
from bs4 import BeautifulSoup
from provider.models import ZlibAccount
from aiohttp import ClientSession


class ZLibCache(CacheService):
    PREFIX = 'ZLIB'
    REDIS_KEYS = {
        'limit': f'{PREFIX}'':{user_id}',
        'available': f'{PREFIX}'':available'
    }
    EX = 60 * 60
    LIMIT = 10

    def incr_limit(self, account_id):
        return self.incr_from_redis(key=self.REDIS_KEYS['limit'].format(user_id=str(account_id)),
                                    ttl=self.EX)

    def get_limit(self, account_id):
        return int(self.get_from_redis(key=self.REDIS_KEYS['limit'].format(user_id=str(account_id))).decode())

    def cache_available(self, account_id):
        return self.cache_on_redis(key=self.REDIS_KEYS['available'], value=account_id, ttl=0)

    def get_available(self):
        return self.get_from_redis(key=self.REDIS_KEYS['available']).decode()


class ZLibService:
    BASE_URL = 'https://zlibrary.org'

    cookies = {
        'proxiesNotWorking': '',
        'domainsNotWorking': '',
        'domains-availability': '%7B%22books%22%3A%22ir1lib.vip%22%2C%22articles%22%3A%22booksc.xyz%22%2C%22'
                                'redirector%22%3A%221lib.domains%22%2C%22singlelogin%22%3A%22singlelogin.app%22%7D',
        'remix_userkey': 'a0a26f56d2f3159b56e729367a39f70b',
        'remix_userid': '6330043',
    }

    headers = {
        'authority': 'zlibrary.org',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                  '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9,fa-IR;q=0.8,fa;q=0.7',
        'referer': 'https://zlibrary.org/s/math?',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/101.0.0.0 Safari/537.36',
    }

    @staticmethod
    def _get_available_account():
        service = ZLibCache()
        account_id = service.get_available()

        if account_id == '0':
            account_id = 1

        if service.get_limit(account_id) < service.LIMIT:
            return ZlibAccount.objects.get(pk=account_id)

        for account in ZlibAccount.objects.all():
            if service.get_limit(account_id=account.id) < service.LIMIT:
                service.cache_available(account_id=account.id)
                return account

    def _fetch_download_url(self, md5: str, session: ClientSession):
        url = f'{self.BASE_URL}/s/{md5.lower()}/'
        account = self._get_available_account()
        self.cookies['remix_userkey'] = account.user_key
        self.cookies['remix_userid'] = str(account.user_id)

        ZLibCache().incr_limit(account_id=account.id)
        res = await session.get(url, headers=self.headers, cookies=self.cookies)
        soup = BeautifulSoup(await res.text(), 'html.parser')
        return soup.find('a', attrs={'class': 'btn btn-primary dlButton addDownloadedBook'})['href']

    def download_book(self, md5, session):
        download_url = f'{self.BASE_URL}{self._fetch_download_url(md5, session)}'
        return session.get(download_url, headers=self.headers, cookies=self.cookies).content
