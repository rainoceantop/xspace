# Generated by Django 2.1.3 on 2019-02-01 11:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyPhoto', '0003_photo_body'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photo',
            name='body',
        ),
    ]
