from _helpers.cache_service import CacheService
from secret import BSCSCAN_API_KEY
from requests.sessions import Session
from .models import CryptoPayment
from bs4 import BeautifulSoup
from .models import Wallet
import re


class PaymentCacheService(CacheService):
    PREFIX = 'PAYMENT'
    REDIS_KEYS = {
        'plan': f'{PREFIX}'':PLAN:{user_id}',
        'network': f'{PREFIX}'':CRYPTO_NETWORK:{user_id}',
    }
    EX = 60 * 60

    def cache_plan(self, user_id, plan_id):
        return self.cache_on_redis(key=self.REDIS_KEYS['plan'].format(user_id=user_id),
                                   value=plan_id,
                                   ttl=self.EX)

    def get_plan(self, user_id):
        return int(self.get_from_redis(key=self.REDIS_KEYS['plan'].format(user_id=user_id)).decode())

    def cache_crypto_network(self, user_id, network):
        return self.cache_on_redis(key=self.REDIS_KEYS['network'].format(user_id=user_id),
                                   value=network,
                                   ttl=self.EX)

    def get_crypto_network(self, user_id):
        return self.get_from_redis(key=self.REDIS_KEYS['network'].format(user_id=user_id)).decode()


class PaymentService:
    BASE_URL = 'https://api.bscscan.com/api'
    BSC_BASE_URL = 'https://bscscan.com'
    BSC_HEADERS = {
        'authority': 'bscscan.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                  '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9,fa-IR;q=0.8,fa;q=0.7',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                      ' (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36',
    }

    @classmethod
    def _request(cls, **kwargs):
        session = Session()
        response = session.get(url=cls.BASE_URL, params=dict(
            apikey=BSCSCAN_API_KEY,
            **kwargs
        ))

        assert response.status_code == 200
        return response.json()

    @classmethod
    def _account(cls, **kwargs):
        return cls._request(module='account',
                            **kwargs)

    @classmethod
    def _transaction(cls, **kwargs):
        return cls._request(module='transaction',
                            **kwargs)

    @classmethod
    def get_tx_list(cls, address):
        return cls._account(action='txlist',
                            startblock=0,
                            endblock=99999999,
                            page=1,
                            sort='desc',
                            address=address)

    @classmethod
    def get_txreceipt_status(cls, tx_hash):
        return cls._transaction(
            action='gettxreceiptstatus',
            txhash=tx_hash
        )

    @classmethod
    def _validate_bsc_tx(cls, tx_hash, minimum_price) -> bool:
        url = f'{cls.BSC_BASE_URL}/tx/{tx_hash}'
        session = Session()

        response = session.get(url=url, headers=cls.BSC_HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.text

        to_address = re.findall(r'To (0x.+?)\s', text)
        amount = re.findall(r'For \d+\.?\d+\s\(\$(\d+\.?\d+)\)', text)

        if not to_address or not amount:
            return False

        to_address = to_address[0]
        amount = float(amount[0])

        wallet = Wallet.objects.filter(network='bep-20').last()
        assert wallet.address == to_address

        if amount < minimum_price:
            return False

        return True

    @classmethod
    def validate_new_bsc_tx(cls, tx_hash, price) -> bool:
        if CryptoPayment.objects.filter(transaction_hash=tx_hash,
                                        approved=True).exists():
            return False
        return cls._validate_bsc_tx(tx_hash=tx_hash,
                                    minimum_price=price + 0.5)
