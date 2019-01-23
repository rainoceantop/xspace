# Generated by Django 2.1.3 on 2019-01-21 07:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.CharField(max_length=22, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('body', models.TextField()),
                ('caption', models.CharField(max_length=4, null=True, verbose_name='photo_column_caption')),
                ('url', models.CharField(max_length=4, null=True, verbose_name='photo_column_url')),
                ('app', models.CharField(default='blog', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blogs', to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
            options={
                'verbose_name': 'Blog',
                'db_table': 'blog',
            },
        ),
        migrations.CreateModel(
            name='BlogReply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.CharField(max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('blog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='MyBlog.Blog')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_replies', to=settings.AUTH_USER_MODEL, to_field='username')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_replied', to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
            options={
                'verbose_name': 'BlogReply',
                'db_table': 'blog_reply',
            },
        ),
        migrations.CreateModel(
            name='BlogSubReply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.CharField(max_length=1000)),
                ('to_reply', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('blog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_replies', to='MyBlog.Blog')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_sub_replies', to=settings.AUTH_USER_MODEL, to_field='username')),
                ('reply', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_replies', to='MyBlog.BlogReply')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_sub_replied', to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
            options={
                'verbose_name': 'BlogSubReply',
                'db_table': 'blog_sub_reply',
            },
        ),
    ]
