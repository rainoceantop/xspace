from django.db import models
from django.contrib.auth.models import User
import uuid
from base64 import urlsafe_b64encode

# Create your models here.


class Blog(models.Model):
    id = models.CharField(primary_key=True, max_length=22, null=False)
    title = models.CharField(max_length=200, null=False)
    body = models.TextField(null=False)
    caption = models.CharField(max_length=4,
                               null=True, verbose_name="photo_column_caption")
    url = models.CharField(max_length=4, null=True,
                           verbose_name="photo_column_url")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blogs', to_field='username')
    app = models.CharField(max_length=10, null=False, default='blog')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blog'
        verbose_name = 'Blog'

    def __str__(self):
        return self.title


class BlogReply(models.Model):
    blog = models.ForeignKey(
        Blog, to_field='id', on_delete=models.CASCADE, related_name='replies')
    body = models.CharField(max_length=1000, null=False)
    from_user = models.ForeignKey(
        User, to_field='username', on_delete=models.CASCADE, related_name='blog_replies')
    to_user = models.ForeignKey(
        User, to_field='username', on_delete=models.CASCADE, related_name='blog_replied')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blog_reply'
        verbose_name = 'BlogReply'

    def __str__(self):
        return self.body


class BlogSubReply(models.Model):
    blog = models.ForeignKey(
        Blog, to_field='id', on_delete=models.CASCADE, related_name='sub_replies')
    reply = models.ForeignKey(BlogReply, to_field='id',
                              on_delete=models.CASCADE, related_name='sub_replies')
    body = models.CharField(max_length=1000, null=False)
    to_reply = models.IntegerField(null=False, default=0)
    from_user = models.ForeignKey(
        User, to_field='username', on_delete=models.CASCADE, related_name='blog_sub_replies')
    to_user = models.ForeignKey(
        User, to_field='username', on_delete=models.CASCADE, related_name='blog_sub_replied')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blog_sub_reply'
        verbose_name = 'BlogSubReply'

    def __str__(self):
        return self.body
