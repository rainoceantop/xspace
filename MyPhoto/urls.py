from django.urls import path
from . import views

app_name = 'myphoto'
urlpatterns = [
    path('upload', views.PhotoUpload.as_view()),
    path('store', views.PhotoStore.as_view()),
    path('<str:id>', views.PhotoGet.as_view()),
    path('<str:username>/photoset', views.PhotoSet.as_view()),
]
