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
    path('getFansAndRequests', views.GetFansAndRequests.as_view()),
    path('followRequest', views.FollowRequest.as_view()),
    path('getMoments', views.GetMoments.as_view()),
    path('getExplores', views.GetExplores.as_view()),
    path('changePasswordByEmail', views.ChangePasswordByEmail.as_view()),
    path('changePasswordCheckToken', views.ChangePasswordCheckToken.as_view()),
    path('changePasswordByEmailConfirm',
         views.ChangePasswordByEmailConfirm.as_view()),
    path('setPrivate', views.SetPrivate.as_view()),
    path('searchUsers', views.SearchUsers.as_view())
]
