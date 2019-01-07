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
