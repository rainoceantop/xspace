from django.http import HttpResponse, JsonResponse
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.hashers import check_password
from django.core.files.storage import FileSystemStorage

import json
import re
import os
import time
from django.core import exceptions
from MyHome.utils import get_redis
from qiniu import Auth as qiniu_auth
from qiniu import put_file, etag, BucketManager, CdnManager
import qiniu.config


# 状态码：信息
# 1：注册成功，返回用户信息
# 2：确认密码与密码不匹配
# 3：用户名已存在
# 4：发生错误
# 6：用户名只能为字母数字组合，有效长度区间为[6-20]位
# 7：密码出现非法字符或长度不在有效区间[8-40]内
# 8：名称有效长度区间[1-20]
class Register(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        password1 = data['password1']
        password2 = data['password2']
        nickname = data['nickname'].strip()

        # username and password pattern
        u_p = r'^[a-zA-Z0-9]{6,20}$'
        p_p = r'^[a-zA-Z0-9,./~!@#$%^&*()_+]{8,40}$'

        # 判断username和密码
        if not re.match(u_p, username):
            return JsonResponse({'code': 6, 'msg': '用户名只能为字母数字组合，有效长度区间为[6-20]位'})
        if not re.match(p_p, password1):
            return JsonResponse({'code': 7, 'msg': '密码出现非法字符或长度不在有效区间[8-40]内'})

        # 判断名称是否太长
        if len(nickname) > 20 or len(nickname) is 0:
            return JsonResponse({'code': 8, 'msg': '名称有效长度区间[1-20]'})

        if password1 == password2:
            if User.objects.filter(username=username).count() is 0:
                try:
                    redis = get_redis()
                    user = User.objects.create_user(
                        username=username,
                        password=password1
                    )
                    redis_key = 'user:{}:detail'.format(user.username)
                    redis.hmset(
                        redis_key, {'username': user.username, 'nickname': nickname, 'avatar': 'http://pkfzvu3bh.bkt.clouddn.com/default.jpg', 'bio': '', 'website': ''})
                    user_detail = get_user_detail(user.username)
                    login(request, user)
                    return JsonResponse({'code': 1, 'msg': user_detail})
                except Exception as e:
                    return JsonResponse({'code': 4, 'msg': '发生错误：{}'.format(e)})
            else:
                return JsonResponse({'code': 3, 'msg': '用户名已存在'})
        else:
            return JsonResponse({'code': 2, 'msg': '确认密码与密码不匹配'})


# 状态码：信息
# 1：登录成功，返回用户信息
# 2：登录失败，账号或密码错误
class Login(View):
    def post(self, request):
        if request.user.is_authenticated:
            logout(request)

        data = json.loads(request.body)
        username = data['username']
        password = data['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            user_detail = get_user_detail(user.username)
            login(request, user)
            return JsonResponse({'code': 1, 'msg': user_detail})
        return JsonResponse({'code': 2, 'msg': '账号或密码错误'})


# 状态码：信息
# 1：注销成功
# 2：用户尚未登录
class Logout(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 2, 'msg': '用户尚未登录'})
        logout(request)
        return JsonResponse({'code': 1, 'msg': '注销成功'})


# 状态码：信息
# 1： 已登录，返回信息
# 2： 未登录
class CheckLogin(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 2, 'msg': '用户尚未登录'})

        user_detail = get_user_detail(request.user.username)
        return JsonResponse({'code': 1, 'msg': user_detail})


class GetUserDetail(View):
    def get(self, request):
        username = request.GET['username']
        user_detail = get_user_detail(username)
        if user_detail:
            redis = get_redis()
            user_detail['followed'] = redis.sismember("user:{}:fans".format(
                username), request.user.username) if request.user.is_authenticated else False
            return JsonResponse({'code': 1, 'msg': user_detail})
        return JsonResponse({'code': 2, 'msg': '找不到该用户'})


class GetFollows(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 2, 'msg': '用户尚未登录'})

        uid = request.GET['uid']
        redis = get_redis()
        redis_key = "user:{}:follows".format(uid)
        follows = redis.smembers(redis_key)
        follows_detail = []
        follow_detail = {}
        for follow in follows:
            follow_key = "user:{}:detail".format(follow.decode())
            if redis.hget(follow_key, 'username') is not None:
                follow_detail['username'] = redis.hget(
                    follow_key, 'username').decode()
                follow_detail['nickname'] = redis.hget(
                    follow_key, 'nickname').decode()
                follow_detail['avatar'] = redis.hget(
                    follow_key, 'avatar').decode()
                follow_detail['bio'] = redis.hget(
                    follow_key, 'bio').decode().replace('<br>', '\n')
                follow_detail['followed'] = redis.sismember(
                    "user:{}:follows".format(request.user.username), follow.decode())
                follows_detail.append(follow_detail)
        return JsonResponse({'code': 1, 'msg': follows_detail})


class GetFans(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 2, 'msg': '用户尚未登录'})

        uid = request.GET['uid']
        redis = get_redis()
        redis_key = "user:{}:fans".format(uid)
        fans = redis.smembers(redis_key)
        fans_detail = []
        fan_detail = {}
        for fan in fans:
            fan_key = "user:{}:detail".format(fan.decode())
            if redis.hget(fan_key, 'username') is not None:
                fan_detail['username'] = redis.hget(
                    fan_key, 'username').decode()
                fan_detail['nickname'] = redis.hget(
                    fan_key, 'nickname').decode()
                fan_detail['avatar'] = redis.hget(fan_key, 'avatar').decode()
                fan_detail['bio'] = redis.hget(
                    fan_key, 'bio').decode().replace('<br>', '\n')
                fan_detail['followed'] = redis.sismember(
                    "user:{}:follows".format(request.user.username), fan.decode())
                fans_detail.append(fan_detail)
        return JsonResponse({'code': 1, 'msg': fans_detail})


class UserFollow(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 2, 'msg': '用户尚未登录'})

        redis = get_redis()
        identity = request.GET['identity']
        fOrUnf = request.GET['fOrUnf']

        if fOrUnf == 'follow':
            redis.sadd("user:{}:follows".format(
                request.user.username), identity)
            redis.sadd("user:{}:fans".format(identity), request.user.username)
        if fOrUnf == 'unfollow':
            redis.srem("user:{}:follows".format(
                request.user.username), identity)
            redis.srem("user:{}:fans".format(identity), request.user.username)

        return JsonResponse({'code': 1, 'msg': '操作成功'})


class ChangePassword(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 2, 'msg': '用户尚未登录'})

        data = json.loads(request.body)
        oldpass = data['oldpass'].strip()
        newpass1 = data['newpass1'].strip()
        newpass2 = data['newpass2'].strip()

        if len(oldpass) is 0 or len(newpass1) is 0 or len(newpass2) is 0:
            return JsonResponse({'code': 3, 'msg': '密码不能为空'})

        p_p = r'^[a-zA-Z0-9,./~!@#$%^&*()_+]{8,40}$'

        if not re.match(p_p, newpass1):
            return JsonResponse({'code': 4, 'msg': '密码出现非法字符或长度不在有效区间[8-40]内'})

        if not newpass1 == newpass2:
            return JsonResponse({'code': 5, 'msg': '新密码与确认密码不匹配'})

        if not check_password(oldpass, request.user.password):
            return JsonResponse({'code': 6, 'msg': '旧密码错误'})

        user = User.objects.get(pk=request.user.id)
        user.set_password(newpass1)
        user.save()
        return JsonResponse({'code': 1, 'msg': '修改成功'})


class ChangeAvatar(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 7, 'msg': '请先登录'})

        avatar_file = request.FILES.get('avatar')
        if not avatar_file:
            return JsonResponse({'code': 2, 'msg': '请选择需要上传的图片'})

        allow_types = ['image/jpeg', 'image/png', 'image/gif']

        if avatar_file.content_type not in allow_types:
            return JsonResponse({'code': 3, 'msg': '上传失败，文件类型错误'})

        file_name = '{}_avatar_{}_{}'.format(
            request.user.username, time.time(), avatar_file.name)
        fs = FileSystemStorage()
        fs.save(file_name, avatar_file)
        file_path = os.path.join(
            os.getcwd(), 'media', file_name).replace('\\', '/')

        access_key = 'M2TrolxfManTFNP4Clr3M12JW0tvAaCV0xIbrZk5'
        secret_key = 'Llh0byt0KDHwiFlcNVvPiTpQSrH8IrZSt5puu1zS'

        q = qiniu_auth(access_key, secret_key)
        bucket_name = 'avatar'
        redis = get_redis()

        try:
            token = q.upload_token(bucket_name, file_name, 3600)
            ret, info = put_file(token, file_name, file_path)
            assert ret['key'] == file_name
            assert ret['hash'] == etag(file_path)
        except Exception as e:
            return JsonResponse({'code': 4, 'msg': '上传文件出错'})
        finally:
            # 删除本地
            fs.delete(file_name)
            # 删除以前头像地址
            used_avatar = redis.hget('user:{}:detail'.format(
                request.user.username), 'avatar').decode()

            if used_avatar != 'http://pkfzvu3bh.bkt.clouddn.com/default.jpg':
                try:
                    bucket = BucketManager(q)
                    key = os.path.basename(used_avatar)
                    ret, info = bucket.delete(bucket_name, key)
                    assert ret == {}
                except Exception as e:
                    pass

            # 更新头像地址
            url = 'http://pkfzvu3bh.bkt.clouddn.com/{}'.format(file_name)
            redis.hset('user:{}:detail'.format(
                request.user.username), 'avatar', url)

            # 刷新缓存
            cdn_manager = CdnManager(q)
            urls = [url]
            cdn_manager.refresh_urls(urls)

            return JsonResponse({'code': 1, 'msg': url})


class GetUpdateData(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 2, 'msg': '用户尚未登录'})

        redis = get_redis()
        redis_key = "user:{}:detail".format(request.user.username)

        data = {
            'nickname': redis.hget(redis_key, 'nickname').decode(),
            'website': redis.hget(redis_key, 'website').decode(),
            'bio': redis.hget(redis_key, 'bio').decode().replace('<br>', '\n'),
            'email': request.user.email,
            'firstname': request.user.first_name
        }
        return JsonResponse({'code': 1, 'msg': data})


class UpdateDetail(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 2, 'msg': '用户尚未登录'})

        data = json.loads(request.body)
        nickname = data['nickname'].strip()
        website = data['website'].strip()
        bio = data['bio'].strip().replace('\n', '<br>')
        email = data['email'].strip()
        firstname = data['firstname'].strip()

        redis = get_redis()

        if len(nickname) > 20 or len(nickname) is 0:
            return JsonResponse({'code': 3, 'msg': '名称有效长度区间[1-20]'})

        if len(bio) > 150:
            return JsonResponse({'code': 3, 'msg': '个人简介有效长度区间[0-150]'})

        w_p = r"^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"

        if len(website) > 0 and not re.match(w_p, website):
            return JsonResponse({'code': 4, 'msg': '网址格式不正确'})

        redis.hmset('user:{}:detail'.format(request.user.username), {
            'nickname': nickname,
            'website': website,
            'bio': bio
        })

        e_p = r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$"
        if len(email) > 0 and not re.match(e_p, email):
            return JsonResponse({'code': 5, 'msg': 'email格式不正确'})

        if len(firstname) > 30:
            return JsonResponse({'code': 6, 'msg': '姓名长度超出区间范围[1-30]'})

        if len(email) > 0 and len(firstname) > 0:
            user = User.objects.get(pk=request.user.id)
            user.email = email
            user.first_name = firstname
            user.save()
        return JsonResponse({'code': 1, 'msg': '更新成功'})


def get_user_detail(uid):
    redis = get_redis()
    redis_key = "user:{}:detail".format(uid)
    user_detail = {
        'username': redis.hget(redis_key, 'username').decode(),
        'nickname': redis.hget(redis_key, 'nickname').decode(),
        'avatar': redis.hget(redis_key, 'avatar').decode(),
        'bio': redis.hget(redis_key, 'bio').decode(),
        'website': redis.hget(redis_key, 'website').decode(),
        'follows': redis.scard("user:{}:follows".format(uid)),
        'fans': redis.scard("user:{}:fans".format(uid)),
    } if redis.hget(redis_key, 'username') is not None else False
    return user_detail
