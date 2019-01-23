from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
# Create your models here.


class Notification(models.Model):
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='actions', to_field='username')
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications', to_field='username')
    action = models.CharField(max_length=20, null=False, default='')
    body = models.CharField(max_length=150, null=False, default='')
    app = models.CharField(max_length=40, null=False, default='photo')
    viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'notification'
        verbose_name = 'Blog'

    def __str__(self):
        return '{}：{}'.format(self.action, self.body)
