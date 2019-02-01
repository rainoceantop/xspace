# Generated by Django 2.1.3 on 2019-01-31 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tag', '0005_auto_20190124_2328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='blogs',
            field=models.ManyToManyField(related_name='b_tags', to='MyBlog.Blog'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='photos',
            field=models.ManyToManyField(related_name='p_tags', to='MyPhoto.Photo'),
        ),
    ]