from django.db.models.signals import post_save
from .models import Photo, PhotoReply, PhotoSubReply
from django.dispatch import receiver
from MyHome.utils import get_redis
from Notification.views import add_notification


@receiver(post_save, sender=Photo)
def add_photo_notification(sender, instance, created, **kwargs):
    if created:
        photo = instance
        redis = get_redis()
        redis_key = 'user:{}:fans'.format(photo.author_id)
        fans = redis.smembers(redis_key)
        fans = [fan.decode() for fan in fans]
        r = add_notification(
            one_or_many='many',
            from_user_id=photo.author_id,
            to_users=fans,
            action='post',
            body='{}发表了新图片'.format(photo.author.last_name),
            app='photo:{}'.format(photo.id)
        )
        print(r)


@receiver(post_save, sender=PhotoReply)
def add_reply_notification(sender, instance, created, **kwargs):
    if created:
        reply = instance
        if not reply.from_user_id == reply.to_user_id:
            r = add_notification(
                one_or_many='one',
                from_user_id=reply.from_user_id,
                to_user_id=reply.to_user_id,
                action='reply',
                body='{}评论了你发表的图片：{}'.format(
                    reply.from_user.last_name, reply.body),
                app='photo:{}'.format(reply.photo.id)
            )
            print(r)


@receiver(post_save, sender=PhotoSubReply)
def add_sub_reply_notification(sender, instance, created, **kwargs):
    if created:
        sub_reply = instance
        if not sub_reply.from_user_id == sub_reply.to_user_id:
            r = add_notification(
                one_or_many='one',
                from_user_id=sub_reply.from_user_id,
                to_user_id=sub_reply.to_user_id,
                action='reply',
                body='{}回复了你的评论：{}'.format(
                    sub_reply.from_user.last_name, sub_reply.body),
                app='photo:{}'.format(sub_reply.photo.id)
            )
            print(r)
