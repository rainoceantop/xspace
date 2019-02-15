from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from MyHome.utils import get_redis


@receiver(post_save, sender=User)
def create_user_detail(sender, instance, created, **kwargs):
    if created:
        user = instance
        redis = get_redis()
        redis_key = 'user:{}:detail'.format(user.username)
        redis.hmset(
            redis_key, {'username': user.username, 'nickname': user.last_name, 'avatar': 'http://pmdz71py1.bkt.clouddn.com/default.jpg', 'bio': '', 'website': '', 'private': 0})
