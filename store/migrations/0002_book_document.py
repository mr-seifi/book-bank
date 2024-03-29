# Generated by Django 4.0.2 on 2022-05-04 10:53

import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
      ALTER TABLE store_book ADD COLUMN document tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(identifier,'')), 'B') ||
        setweight(to_tsvector('english', coalesce(authors,'')), 'C') ||
        setweight(to_tsvector('english', coalesce(publisher,'')), 'C') ||
        setweight(to_tsvector('english', coalesce(description,'')), 'D')
      ) STORED;
    ''',

            reverse_sql='''
      ALTER TABLE store_book DROP COLUMN document;
    ''',
            state_operations=[
                migrations.AddField(
                    model_name='book',
                    name='document',
                    field=django.contrib.postgres.search.SearchVectorField(null=True, blank=True),
                ),
            ]
        ),
    ]
