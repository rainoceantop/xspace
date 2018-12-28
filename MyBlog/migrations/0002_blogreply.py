# Generated by Django 2.1.3 on 2018-12-12 13:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('MyBlog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogReply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.CharField(max_length=1000)),
                ('to_reply', models.IntegerField(default=0)),
                ('blog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='MyBlog.Blog')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_replies', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_replied', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
