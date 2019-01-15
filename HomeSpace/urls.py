from django.urls import path
from . import views

app_name = 'homespace'
urlpatterns = [
    path('register', views.Register.as_view()),
    path('login', views.Login.as_view()),
    path('logout', views.Logout.as_view()),
    path('checkLogin', views.CheckLogin.as_view()),
    path('getUserDetail', views.GetUserDetail.as_view()),
    path('userFollow', views.UserFollow.as_view()),
    path('changePassword', views.ChangePassword.as_view()),
    path('changeAvatar', views.ChangeAvatar.as_view()),
    path('updateDetail', views.UpdateDetail.as_view()),
    path('getUpdateData', views.GetUpdateData.as_view()),
    path('getFollows', views.GetFollows.as_view()),
    path('getFans', views.GetFans.as_view()),
    path('getMoments', views.GetMoments.as_view()),
    path('getExplores', views.getExplores.as_view())
]
