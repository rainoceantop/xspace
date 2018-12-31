from django.db import models
from django.contrib.auth.models import User
from base64 import urlsafe_b64encode

# Create your models here.


class Blog(models.Model):
    title = models.CharField(max_length=200, null=False)
    body = models.TextField(null=False)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blogs', to_field='id')
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
    to_reply = models.IntegerField(null=False, default=0)
    parent_reply = models.IntegerField(null=False, default=0)
    from_user = models.ForeignKey(
        User, to_field='id', on_delete=models.CASCADE, related_name='my_replies')
    to_user = models.ForeignKey(
        User, to_field='id', on_delete=models.CASCADE, related_name='my_replied')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blog_reply'
        verbose_name = 'BlogReply'

    def __str__(self):
        return self.body
