# Generated by Django 2.2.11 on 2020-05-11 09:21

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ("rango", "0005_page_last_visit"),
    ]

    operations = [
        migrations.AlterField(
            model_name="page",
            name="last_visit",
            field=models.DateTimeField(
                default=datetime.datetime(2020, 5, 11, 9, 21, 59, 397941, tzinfo=utc)
            ),
        ),
    ]
