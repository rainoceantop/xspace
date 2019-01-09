from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Photo(models.Model):
    id = models.CharField(primary_key=True, max_length=22, null=False)
    title = models.CharField(max_length=50, null=False, default='')
    caption = models.CharField(max_length=500, null=False)
    url = models.URLField(null=False)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='photos', to_field='username')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'photo'
        verbose_name = 'photo'

    def __str__(self):
        return self.id


class PhotoReply(models.Model):
    photo = models.ForeignKey(
        Photo, to_field='id', on_delete=models.CASCADE, related_name='replies')
    body = models.CharField(max_length=1000, null=False)
    from_user = models.ForeignKey(
        User, to_field='username', on_delete=models.CASCADE, related_name='photo_replies')
    to_user = models.ForeignKey(
        User, to_field='username', on_delete=models.CASCADE, related_name='photo_replied')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'photo_reply'
        verbose_name = 'PhotoReply'

    def __str__(self):
        return self.body


class PhotoSubReply(models.Model):
    photo = models.ForeignKey(
        Photo, to_field='id', on_delete=models.CASCADE, related_name='sub_replies')
    reply = models.ForeignKey(PhotoReply, to_field='id',
                              on_delete=models.CASCADE, related_name='sub_replies')
    body = models.CharField(max_length=1000, null=False)
    to_reply = models.IntegerField(null=False, default=0)
    parent_reply = models.IntegerField(null=False, default=0)
    from_user = models.ForeignKey(
        User, to_field='username', on_delete=models.CASCADE, related_name='photo_sub_replies')
    to_user = models.ForeignKey(
        User, to_field='username', on_delete=models.CASCADE, related_name='photo_sub_replied')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'photo_sub_reply'
        verbose_name = 'PhotoSubReply'

    def __str__(self):
        return self.body
