from django.urls import path
from . import views

app_name = 'myphoto'
urlpatterns = [
    path('upload', views.PhotoUpload.as_view()),
    path('store', views.PhotoStore.as_view()),
    path('likes', views.PhotoAndReplyLikes.as_view()),

    path('replyStore', views.PhotoReplyStore.as_view()),
    path('subReplyStore', views.PhotoSubReplyStore.as_view()),
    path('likes', views.PhotoAndReplyLikes.as_view()),
    path('reply', views.PhotoReplyGet.as_view()),
    path('subReply', views.PhotoSubReplyGet.as_view()),
    path('reply/<int:id>/delete', views.PhotoReplyDelete.as_view()),

    path('<str:id>', views.PhotoGet.as_view()),
    path('<str:username>/photoset', views.PhotoSet.as_view()),
]
