# Generated by Django 2.2.11 on 2020-03-31 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rango", "0002_auto_20200331_0941"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="slug",
            field=models.SlugField(default=""),
            preserve_default=False,
        ),
    ]
