from django.http import HttpResponse, JsonResponse
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.hashers import check_password
from django.core.files.storage import FileSystemStorage

import json
import re
import os
from django.core import exceptions
from MyHome.utils import get_redis
from qiniu import Auth as qiniu_auth
from qiniu import put_file, etag, BucketManager
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
                    redis_key = 'user:{}:detail'.format(user.id)
                    redis.hmset(
                        redis_key, {'id': user.id, 'nickname': nickname, 'avatar': 'http://pkfzvu3bh.bkt.clouddn.com/default.jpg', 'bio': '', 'website': ''})
                    user_detail = get_user_detail(user.id)
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
            user_detail = get_user_detail(user.id)
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

        user_detail = get_user_detail(request.user.id)
        return JsonResponse({'code': 1, 'msg': user_detail})


class GetUserDetail(View):
    def get(self, request):
        uid = request.GET['uid']
        user_detail = get_user_detail(uid)
        if user_detail:
            redis = get_redis()
            user_detail['followed'] = redis.sismember("user:{}:fans".format(
                uid), request.user.id) if request.user.is_authenticated else False
            return JsonResponse({'code': 1, 'msg': user_detail})
        return JsonResponse({'code': 2, 'msg': '找不到该用户'})


class UserFollow(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 2, 'msg': '用户尚未登录'})

        redis = get_redis()
        identity = request.GET['identity']
        fOrUnf = request.GET['fOrUnf']

        if fOrUnf == 'follow':
            redis.sadd("user:{}:follows".format(request.user.id), identity)
            redis.sadd("user:{}:fans".format(identity), request.user.id)
        if fOrUnf == 'unfollow':
            redis.srem("user:{}:follows".format(request.user.id), identity)
            redis.srem("user:{}:fans".format(identity), request.user.id)

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
        # return JsonResponse({'id': request.user.id})

        if not request.user.is_authenticated:
            return JsonResponse({'code': 7, 'msg': '请先登录'})

        # avatar_file = request.FILES.get('avatar')
        # if not avatar_file:
        #     return JsonResponse({'code': 2, 'msg': '请选择需要上传的图片'})

        return JsonResponse({'id': request.FILES.get('avatar') is None})

        # allow_types = ['image/jpeg', 'image/png', 'image/gif']

        # if avatar_file.content_type not in allow_types:
        #     return JsonResponse({'code': 3, 'msg': '上传失败，文件类型错误'})

        # file_name = '{}_avatar'.format(request.user.id)
        # fs = FileSystemStorage()
        # fs.save(file_name, avatar_file)
        # file_path = os.path.join(
        #     os.getcwd(), 'media', file_name).replace('\\', '/')

        # access_key = 'M2TrolxfManTFNP4Clr3M12JW0tvAaCV0xIbrZk5'
        # secret_key = 'Llh0byt0KDHwiFlcNVvPiTpQSrH8IrZSt5puu1zS'

        # q = qiniu_auth(access_key, secret_key)
        # bucket_name = 'avatar'
        # redis = get_redis()

        # try:
        #     token = q.upload_token(bucket_name, file_name, 3600)
        #     ret, info = put_file(token, file_name, file_path)
        #     assert ret['key'] == file_name
        #     assert ret['hash'] == etag(file_path)
        # except Exception as e:
        #     return JsonResponse({'code': 4, 'msg': '上传文件出错'})
        # finally:
        #     # 删除本地
        #     fs.delete(file_name)
        #     # 删除以前的头像
        #     used_avatar = redis.hget('user:{}:detail'.format(
        #         request.user.id), 'avatar').decode()
        #     if used_avatar != 'http://pkfzvu3bh.bkt.clouddn.com/default.jpg':
        #         try:
        #             ret, info = bucket.delete(bucket_name, used_avatar)
        #             assert ret == {}
        #         except Exception as e:
        #             return JsonResponse({'code': 5, 'msg': '删除失败，找不到该文件'})
        #     # 更新头像地址
        #     url = 'http://pkfzvu3bh.bkt.clouddn.com/{}'.format(file_name)
        #     redis.hset('user:{}:detail'.format(
        #         request.user.id), {'avatar': url})
        #     return JsonResponse({'code': 1, 'url': url})


class GetUpdateData(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 2, 'msg': '用户尚未登录'})

        redis = get_redis()
        redis_key = "user:{}:detail".format(request.user.id)

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

        redis.hmset('user:{}:detail'.format(request.user.id), {
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
        'id': int(redis.hget(redis_key, 'id').decode()),
        'nickname': redis.hget(redis_key, 'nickname').decode(),
        'avatar': redis.hget(redis_key, 'avatar').decode(),
        'bio': redis.hget(redis_key, 'bio').decode(),
        'website': redis.hget(redis_key, 'website').decode(),
        'follows': redis.scard("user:{}:follows".format(uid)),
        'fans': redis.scard("user:{}:fans".format(uid)),
    } if redis.hget(redis_key, 'id') is not None else False
    return user_detail
