from django.urls import path
from . import views

app_name = 'tag'
urlpatterns = [
    path('searchTags', views.SearchTags.as_view())
]
