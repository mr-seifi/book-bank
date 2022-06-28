class RedirectService:

    BASE_URL = 'https://book-bank.net/download'

    def generate_redirect_url(self, book):
        if not book.download_url:
            return

        second_part_url = book.download_url.split('main/')[1]
        return f'{self.BASE_URL}/book/{second_part_url}'
