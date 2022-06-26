from django.views.generic import RedirectView
from store.models import Book
from django.shortcuts import get_object_or_404
from django.conf import settings


class BookDownloadUrlRedirectView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        md5 = kwargs.get('md5')
        if not md5:
            return

        book = get_object_or_404(Book, md5=md5)
        if book.filesize < settings.DOWNLOAD_LIMIT_SIZE:
            return

        return book.download_url
