from django.db import models
from MyPhoto.models import Photo
from MyBlog.models import Blog

# Create your models here.


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)
    photos = models.ManyToManyField(Photo, related_name='tags')
    blogs = models.ManyToManyField(Blog, related_name='tags')

    class Meta:
        db_table = 'tag'
        verbose_name = 'Tag'

    def __str__(self):
        return self.name
