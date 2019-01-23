from django.urls import path
from . import views

app_name = 'notification'
urlpatterns = [
    path('getNotifyCount', views.GetNotifyCount.as_view()),
    path('getNotifications', views.GetNotification.as_view()),
    path('deleteNotifications', views.DeleteNotification.as_view()),
]
