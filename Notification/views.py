from django.shortcuts import render
from django.views import View
from .models import Notification
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.db.models import Q
from MyHome.utils import get_redis, ConvertTime
# Create your views here.


class GetNotifyCount(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '用户尚未登录'})

        notify_count = Notification.objects.filter(
            Q(to_user_id=request.user.username) & Q(viewed=False)).count()
        return JsonResponse({'code': 1, 'msg': notify_count})


class GetNotification(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '用户尚未登录'})

        notifications = Notification.objects.filter(
            to_user_id=request.user.username).order_by('-created_at')

        notification_list = []

        if notifications:
            redis = get_redis()
            ct = ConvertTime()
            notification_list = [{
                'id': notification.id,
                'from_user_id': notification.from_user.username,
                'from_user_avatar': redis.hget('user:{}:detail'.format(notification.from_user.username), 'avatar').decode(),
                'body': notification.body,
                'app': notification.app,
                'viewed': notification.viewed,
                'created_at': ct.convertDatetime(notification.created_at)
            } for notification in notifications]

            notifications.update(viewed=True)

        return JsonResponse({'code': 1, 'msg': notification_list})


class DeleteNotification(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '用户尚未登录'})
        Notification.objects.filter(
            to_user_id=request.user.username).delete()
        return JsonResponse({'code': 1, 'msg': '删除成功'})


class AddNotification(View):
    pass


def add_notification(**kwargs):
    one_or_many = kwargs['one_or_many']
    from_user_id = kwargs['from_user_id']
    action = kwargs['action']
    body = kwargs['body']
    app = kwargs['app']
    expires_at = datetime.now() + timedelta(30)
    try:
        if one_or_many == 'one':
            to_user_id = kwargs['to_user_id']
            Notification.objects.create(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                action=action,
                body=body,
                app=app,
                expires_at=expires_at
            )
        if one_or_many == 'many':
            to_users = kwargs['to_users']
            n_list = [Notification(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                action=action,
                body=body,
                app=app,
                expires_at=expires_at
            ) for to_user_id in to_users]

            Notification.objects.bulk_create(n_list)

        return True
    except Exception as e:
        return e
