from django.urls import path
from . import views

app_name = 'myblog'
urlpatterns = [
    path('store', views.BlogStore.as_view()),
    path('<str:id>', views.BlogGet.as_view()),
    path('<str:username>/blogset', views.BlogSet.as_view()),
    path('<str:id>/update', views.BlogUpdate.as_view()),
    path('<str:id>/delete', views.BlogDelete.as_view()),
    path('fileupload', views.BlogFileUpload.as_view()),
    path('replyStore', views.BlogReplyStore.as_view()),
    path('reply/<int:id>/delete', views.BlogReplyDelete.as_view()),
    path('likes', views.BlogAndReplyLikes.as_view())
]
