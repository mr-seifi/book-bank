from django.views.generic import RedirectView
from store.models import Book
from django.shortcuts import get_object_or_404


class BookDownloadUrlRedirectView(RedirectView):

    DOWNLOAD_LIMIT_SIZE = int(7e7)

    def get_redirect_url(self, *args, **kwargs):
        md5 = kwargs.get('md5')
        if not md5:
            return

        book = get_object_or_404(Book, md5=md5)
        if book.filesize < self.DOWNLOAD_LIMIT_SIZE:
            return

        return book.download_url
