# Generated by Django 2.1.3 on 2019-01-21 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Notification', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='app',
            field=models.CharField(default='photo', max_length=25),
        ),
    ]
