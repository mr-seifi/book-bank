from django.core.validators import MinValueValidator
from django.db import models, connections, transaction
from django.db.models import AutoField
from django.utils.functional import partition
from django.utils.text import slugify
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.core.files.base import ContentFile
import requests


class BookQuerySet(models.QuerySet):
    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        if batch_size is not None and batch_size <= 0:
            raise ValueError("Batch size must be a positive integer.")

        for parent in self.model._meta.get_parent_list():
            if parent._meta.concrete_model is not self.model._meta.concrete_model:
                raise ValueError("Can't bulk create a multi-table inherited model")
        if not objs:
            return objs
        self._for_write = True
        connection = connections[self.db]
        opts = self.model._meta
        fields = opts.concrete_fields[:21] + opts.concrete_fields[22:]
        objs = list(objs)
        self._prepare_for_bulk_create(objs)
        with transaction.atomic(using=self.db, savepoint=False):
            objs_with_pk, objs_without_pk = partition(lambda o: o.pk is None, objs)
            if objs_with_pk:
                returned_columns = self._batched_insert(
                    objs_with_pk,
                    fields,
                    batch_size,
                    ignore_conflicts=ignore_conflicts,
                )
                for obj_with_pk, results in zip(objs_with_pk, returned_columns):
                    for result, field in zip(results, opts.db_returning_fields):
                        if field != opts.pk:
                            setattr(obj_with_pk, field.attname, result)
                for obj_with_pk in objs_with_pk:
                    obj_with_pk._state.adding = False
                    obj_with_pk._state.db = self.db
            if objs_without_pk:
                fields = [f for f in fields if not isinstance(f, AutoField)]
                returned_columns = self._batched_insert(
                    objs_without_pk,
                    fields,
                    batch_size,
                    ignore_conflicts=ignore_conflicts,
                )
                if (
                        connection.features.can_return_rows_from_bulk_insert
                        and not ignore_conflicts
                ):
                    assert len(returned_columns) == len(objs_without_pk)
                for obj_without_pk, results in zip(objs_without_pk, returned_columns):
                    for result, field in zip(results, opts.db_returning_fields):
                        setattr(obj_without_pk, field.attname, result)
                    obj_without_pk._state.adding = False
                    obj_without_pk._state.db = self.db

        return objs


class BookManager(models.Manager):
    def get_queryset(self):
        return BookQuerySet(self.model, using=self._db)


class Book(models.Model):
    class Languages(models.TextChoices):
        ENGLISH = 'English', 'en'
        RUSSIAN = 'Russian', 'ru'
        FRENCH = 'French', 'fr'
        SPANISH = 'Spanish', 'es'
        GERMAN = 'German', 'de'
        ITALIAN = 'Italian', 'it'

    class Extensions(models.TextChoices):
        PDF = 'pdf', 'PDF'
        EPUB = 'epub', 'EPUB'
        DJVU = 'djvu', 'DJVU'
        DOC = 'doc', 'DOC',
        mobi = 'mobi', 'MOBI',
        rar = 'rar', 'RAR',
        zip = 'zip', 'ZIP'
        azw3 = 'azw3', 'AZW3'

    libgen_id = models.IntegerField(unique=True, default=-1)
    title = models.TextField()
    slug = models.SlugField(max_length=5000, blank=True)
    description = models.TextField(null=True, blank=True)
    series = models.TextField(null=True, blank=True)
    publisher = models.TextField(null=True, blank=True)
    authors = models.TextField(null=True, blank=True)
    year = models.TextField(max_length=300, blank=True, null=True)
    edition = models.TextField(blank=True)
    pages = models.TextField(null=True, blank=True)
    language = models.CharField(max_length=50, choices=Languages.choices, default=Languages.ENGLISH)
    topic = models.TextField(default='Other')
    cover_url = models.URLField(max_length=2000, null=True, blank=True)
    cover = models.ImageField(upload_to='covers', max_length=5000, null=True, blank=True)
    identifier = models.TextField(blank=True)
    md5 = models.CharField(max_length=300, blank=True)
    filesize = models.IntegerField(validators=[MinValueValidator(0)])
    extension = models.CharField(max_length=50, choices=Extensions.choices, default=Extensions.PDF)
    download_url = models.URLField(max_length=2000, blank=True, null=True)
    file = models.CharField(max_length=50, blank=True, null=True)
    document = SearchVectorField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = BookManager()

    class Meta:
        indexes = [
            models.Index(fields=['libgen_id']),
            models.Index(fields=['title']),
            models.Index(fields=['slug']),
            models.Index(fields=['identifier']),
            models.Index(fields=['authors']),
            models.Index(fields=['publisher']),
            GinIndex(fields=['document']),
        ]

    def __str__(self):
        return self.title

    def _do_insert(self, manager, using, fields, returning_fields, raw):
        return super(Book, self)._do_insert(manager,
                                            using,
                                            [f for f in fields if f.attname != 'document'],
                                            returning_fields,
                                            raw)

    def _do_update(self, base_qs, using, pk_val, values, update_fields, forced_update):
        return super(Book, self)._do_update(base_qs,
                                            using,
                                            pk_val,
                                            [value for value in values if value[0].name != 'document'],
                                            update_fields,
                                            forced_update)

    def download_cover(self, session: requests.Session):
        content = ContentFile(session.get(self.cover_url).content)
        self.cover.save(name=f'{self.slug}.{self.cover_url.split(".")[-1]}', content=content, save=True)

    def save(self, *args, **kwargs):
        if self.cover:
            cover_extension = self.cover.name.split('.')[-1]
            self.cover.name = f'{self.slug}.{cover_extension}'
        if self.topic:
            self.topic = slugify(self.topic.replace('\\', ' '))
        if not self.slug:
            self.slug = slugify(f'{self.title} {self.publisher} {self.year}')
        super(Book, self).save(*args, **kwargs)
