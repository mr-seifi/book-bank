class RedirectService:

    BASE_URL = 'https://book-bank.net/download'

    def generate_redirect_url(self, book):
        return f'{self.BASE_URL}/{book.md5}/'
