# Generated by Django 2.1.3 on 2019-01-12 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyPhoto', '0009_auto_20190108_1547'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='app',
            field=models.CharField(default='photo', max_length=10),
        ),
        migrations.AddField(
            model_name='photo',
            name='body',
            field=models.CharField(max_length=4, null=True, verbose_name='blog_column_body'),
        ),
    ]