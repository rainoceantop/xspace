from django.http import HttpResponse, JsonResponse
from django.views import View
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.core.mail import send_mail
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.hashers import check_password
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q, F, Count

from MyBlog.models import Blog
from MyPhoto.models import Photo
import json
import re
import os
import time
from base64 import urlsafe_b64encode, urlsafe_b64decode
from django.core import exceptions
from MyHome.utils import get_redis, ConvertTime
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
                    user = User.objects.create_user(
                        username=username,
                        password=password1,
                        last_name=nickname
                    )
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
        for follow in follows:
            follow_key = "user:{}:detail".format(follow.decode())
            follow_detail = {}
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
        for fan in fans:
            fan_key = "user:{}:detail".format(fan.decode())
            fan_detail = {}
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


class ChangePasswordByEmail(View):
    def get(self, request):
        email = request.GET['email']

        user = User.objects.filter(
            Q(username=email) | Q(email=email)).first()
        if user:
            uid = urlsafe_b64encode(user.username.encode()).decode()
            token = default_token_generator.make_token(user)
            url = 'http://192.168.1.7:8080/accounts/password/reset/confirm/{}/{}'.format(
                uid, token)
            r = send_mail(
                'Xspace',
                '嘿，你需要修改密码，点击链接"{}"'.format(url),
                'jessensl77@163.com',
                [user.email],
                fail_silently=False
            )
            print(user.email)
            print(r)
            return JsonResponse({'code': 1, 'msg': '发送成功'})

        return JsonResponse({'code': 2, 'msg': '出错，未查询到相关账号'})


class ChangePasswordCheckToken(View):
    def get(self, request):
        uid = request.GET['uid']
        token = request.GET['token']
        username = urlsafe_b64decode(uid).decode()
        try:
            user = User.objects.get(username=username)
            c = default_token_generator.check_token(user, token)
            if c:
                return JsonResponse({'code': 1, 'msg': '认证成功'})
            return JsonResponse({'code': 2, 'msg': 'token认证失败'})
        except exceptions.ObjectDoesNotExist:
            return JsonResponse({'code': 2, 'msg': '用户认证失败'})


class ChangePasswordByEmailConfirm(View):
    def post(self, request):
        uid = request.GET['uid']
        token = request.GET['token']
        username = urlsafe_b64decode(uid).decode()
        try:
            user = User.objects.get(username=username)
            c = default_token_generator.check_token(user, token)
            if not c:
                return JsonResponse({'code': 2, 'msg': 'token认证失败'})

            data = json.loads(request.body)
            newpass1 = data['newpass1'].strip()
            newpass2 = data['newpass2'].strip()
            if len(newpass1) is 0 or len(newpass2) is 0:
                return JsonResponse({'code': 3, 'msg': '密码不能为空'})

            p_p = r'^[a-zA-Z0-9,./~!@#$%^&*()_+]{8,40}$'

            if not re.match(p_p, newpass1):
                return JsonResponse({'code': 4, 'msg': '密码出现非法字符或长度不在有效区间[8-40]内'})

            if not newpass1 == newpass2:
                return JsonResponse({'code': 5, 'msg': '新密码与确认密码不匹配'})
            user.set_password(newpass1)
            user.save()
            login(request, user)
            return JsonResponse({'code': 1, 'msg': get_user_detail(user.username)})

        except exceptions.ObjectDoesNotExist:
            return JsonResponse({'code': 2, 'msg': '用户认证失败'})


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

        if len(email) > 0 or len(firstname) > 0:
            user = User.objects.get(pk=request.user.id)
            user.email = email
            user.first_name = firstname
            user.save()
        return JsonResponse({'code': 1, 'msg': '更新成功'})


class GetMoments(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 2, 'msg': '用户尚未登录'})

        redis = get_redis()
        ct = ConvertTime()
        follows = redis.smembers(
            'user:{}:follows'.format(request.user.username))
        follows = [follow.decode() for follow in follows]
        follows.append(request.user.username)
        moments = Blog.objects.annotate(replies_count=Count('replies')).filter(author_id__in=follows).union(
            Photo.objects.annotate(replies_count=Count('replies')).filter(author_id__in=follows)).order_by('-created_at')
        items = []
        for r in moments:
            item = {}
            item['id'] = r.id
            item['title'] = r.title
            item['app'] = r.app
            item['author_id'] = r.author_id
            item['created_at'] = ct.convertDatetime(r.created_at)
            item['author'] = redis.hget("user:{}:detail".format(
                r.author_id), 'nickname').decode()
            item['author_avatar'] = redis.hget(
                "user:{}:detail".format(r.author_id), 'avatar').decode()
            item['replies_count'] = r.replies_count
            item['replies'] = []
            if r.app == 'photo':
                item['url'] = r.url
                item['caption'] = r.caption
                item['likes'] = redis.scard('photo:{}:likes'.format(r.id))
                item['liked'] = redis.sismember(
                    'photo:{}:likes'.format(r.id), request.user.username)
            if r.app == 'blog':
                item['body'] = r.body
                item['likes'] = redis.scard('blog:{}:likes'.format(r.id))
                item['liked'] = redis.sismember(
                    'blog:{}:likes'.format(r.id), request.user.username)
            items.append(item)
        return JsonResponse({'code': 1, 'msg': items})


class getExplores(View):
    def get(self, request):
        explores = Blog.objects.annotate(Count('replies', distinct=True), Count('sub_replies', distinct=True)).union(
            Photo.objects.annotate(Count('replies', distinct=True), Count('sub_replies', distinct=True))).order_by('-created_at')

        if explores:
            redis = get_redis()
            items = []
            for r in explores:
                item = {}
                item['id'] = r.id
                item['app'] = r.app
                item['replies_count'] = r.replies__count
                item['sub_replies_count'] = r.sub_replies__count
                if r.app == 'photo':
                    item['url'] = r.url
                    item['likes'] = redis.scard('photo:{}:likes'.format(r.id))
                if r.app == 'blog':
                    item['title'] = r.title
                    item['likes'] = redis.scard('blog:{}:likes'.format(r.id))
                items.append(item)
            return JsonResponse({'code': 1, 'msg': items})
        return JsonResponse({'code': 2, 'msg': '暂无数据'})


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
