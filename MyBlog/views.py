from django.http import HttpResponse, JsonResponse
from django.views import View
from .models import Blog, BlogReply, BlogSubReply
from django.contrib.auth.models import User
from django.core import serializers, exceptions
from django.core.files.storage import FileSystemStorage
from django.core.cache import cache
from django_redis import get_redis_connection
from django.db.models import Q, F
from MyHome.utils import ConvertTime, get_redis, get_uuid_base64

import json
import re
import time
import os

from qiniu import Auth as qiniu_auth
from qiniu import put_file, etag
import qiniu.config


# 状态码：信息
# 1：获取成功，返回blog数据
# 2：获取失败，找不到该博客
class BlogGet(View):
    def get(self, request, id):
        redis = get_redis()
        ct = ConvertTime()
        try:
            blog = Blog.objects.get(pk=id)

            redis_blog_user_key = "user:{}:detail".format(blog.author_id)

            blog = {
                'id': blog.id,
                'author_id': blog.author_id,
                'title': blog.title,
                'body': blog.body,
                'created_at': ct.convertDatetime(blog.created_at),
                'author': redis.hget(redis_blog_user_key, 'nickname').decode(),
                'author_avatar': redis.hget(redis_blog_user_key, 'avatar').decode(),
                'author_follows': redis.scard("user:{}:follows".format(blog.author_id)),
                'author_fans': redis.scard("user:{}:fans".format(blog.author_id)),
                'replies_count': blog.replies.count() + blog.sub_replies.count(),
                'likes': redis.scard('blog:{}:likes'.format(blog.id)),
                'liked': redis.sismember('blog:{}:likes'.format(blog.id), request.user.username) if request.user.is_authenticated else False
            }

            return JsonResponse({'code': 1, 'msg': blog, 'addition': ['']})
        except exceptions.ObjectDoesNotExist:
            return JsonResponse({'code': 2, 'msg': '找不到该博客'})


# 获取blog set
class BlogSet(View):
    def get(self, request, username):
        blog_set = Blog.objects.filter(
            author_id=username).order_by('-created_at')
        if blog_set:
            blogs = [{
                'id': blog.id,
                'title': blog.title
            } for blog in blog_set]

            return JsonResponse({'code': 1, 'msg': blogs})
        return JsonResponse({'code': 2, 'msg': '未找到相关博客'})


# 创建blog
class BlogStore(View):
    def post(self, request):
        # 判断是否已经登陆
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '创建博客请先登录'})

        data = json.loads(request.body)
        title = data['title'].strip()
        body = data['body'].strip()

        if len(title) > 100 or len(title) < 1:
            return JsonResponse({'code': 3, 'msg': '标题不能为空且不超过100个字符'})
        if len(body) < 100:
            return JsonResponse({'code': 5, 'msg': 'Oh,come on,it is a blog!内容不得小于100个字符'})

        blog = Blog.objects.create(
            id=get_uuid_base64(),
            title=title,
            body=body,
            author_id=request.user.username
        )
        return JsonResponse({'code': 1, 'msg': {'id': blog.id, 'title': blog.title}})


# 修改blog
class BlogUpdate(View):
    def post(self, request, id):
        # 判断是否已经登陆
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '修改博客请先登录'})

        data = json.loads(request.body)
        title = data['title'].strip()
        body = data['body'].strip()

        if len(title) > 100 or len(title) < 1:
            return JsonResponse({'code': 3, 'msg': '标题不能为空且不超过100个字符'})
        if len(body) < 100:
            return JsonResponse({'code': 5, 'msg': 'Oh,come on,it is a blog!内容不得小于100个字符'})

        try:
            blog = Blog.objects.get(pk=id)
            if blog.author_id == request.user.username:
                blog.title = title
                blog.body = body
                blog.save()
                return JsonResponse({'code': 1, 'msg': blog.id})
            return JsonResponse({'code': 8, 'msg': '修改失败，无权修改'})
        except exceptions.ObjectDoesNotExist:
            return JsonResponse({'code': 2, 'msg': '修改失败，没有该博客'})


# 删除blog
class BlogDelete(View):
    def get(self, request, id):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '请先登录再进行操作'})
        try:
            blog = Blog.objects.get(pk=id)
            redis = get_redis()
            if blog.author_id == request.user.username:
                # 删除该博客的所有评论点赞数
                for r in blog.replies.all():
                    redis.delete('breply:{}:likes'.format(r.id))
                for r in blog.sub_replies.all():
                    redis.delete('bsreply:{}:likes'.format(r.id))

                # 删除博客点赞
                redis.delete('blog:{}:likes'.format(id))

                # 删除博客
                blog.delete()
                return JsonResponse({'code': 1, 'msg': '删除成功'})
            return JsonResponse({'code': 3, 'msg': '删除失败，无权删除'})
        except exceptions.ObjectDoesNotExist:
            return JsonResponse({'code': 2, 'msg': '删除失败，没有该博客'})


class BlogFileUpload(View):
    def post(self, request):
        blog_file = request.FILES.get('upload')
        if not blog_file:
            return JsonResponse({'uploaded': False, 'msg': '上传文件出错'})

        allow_types = ['image/jpeg', 'image/png', 'image/gif']

        if blog_file.content_type not in allow_types:
            return JsonResponse({'uploaded': False, 'msg': '文件类型错误'})

        file_name = '{}_{}'.format(str(time.time()), blog_file.name)
        fs = FileSystemStorage()
        fs.save(file_name, blog_file)
        file_path = os.path.join(
            os.getcwd(), 'media', file_name).replace('\\', '/')

        access_key = 'M2TrolxfManTFNP4Clr3M12JW0tvAaCV0xIbrZk5'
        secret_key = 'Llh0byt0KDHwiFlcNVvPiTpQSrH8IrZSt5puu1zS'

        q = qiniu_auth(access_key, secret_key)
        bucket_name = 'blog2'

        try:
            token = q.upload_token(bucket_name, file_name, 3600)
            ret, info = put_file(token, file_name, file_path)
            assert ret['key'] == file_name
            assert ret['hash'] == etag(file_path)
        except Exception as e:
            return JsonResponse({'uploaded': False, 'msg': '上传文件出错'})
        finally:
            fs.delete(file_name)
            return JsonResponse({'uploaded': True, 'url': 'http://pldd64kvs.bkt.clouddn.com/{}'.format(file_name)})


class BlogReplyGet(View):
    def get(self, request):
        blog_id = request.GET['id']
        replies = BlogReply.objects.filter(
            blog_id=blog_id)[:10]
        if replies:
            redis = get_redis()
            ct = ConvertTime()
            replies = [{
                'id': reply.id,
                'body': reply.body,
                'from_user_id': reply.from_user_id,
                'from_user_nickname': redis.hget("user:{}:detail".format(reply.from_user_id), "nickname").decode(),
                'from_user_avatar': redis.hget("user:{}:detail".format(reply.from_user_id), "avatar").decode(),
                'to_user_id': reply.to_user_id,
                'created_at': ct.convertDatetime(reply.created_at),
                'sub_replies_count': reply.sub_replies.count(),
                'likes': redis.scard('breply:{}:likes'.format(reply.id)),
                'liked': redis.sismember('breply:{}:likes'.format(reply.id), request.user.username) if request.user.is_authenticated else False
            } for reply in replies]
        else:
            replies = []

        return JsonResponse({'code': 1, 'msg': replies})


class BlogSubReplyGet(View):
    def get(self, request):
        reply_id = request.GET['id']
        replies = BlogSubReply.objects.filter(
            reply_id=reply_id)[:10]
        if replies:
            redis = get_redis()
            ct = ConvertTime()
            replies = [{
                'id': reply.id,
                'reply_id': reply.reply_id,
                'body': reply.body,
                'from_user_id': reply.from_user_id,
                'from_user_nickname': redis.hget("user:{}:detail".format(reply.from_user_id), "nickname").decode(),
                'from_user_avatar': redis.hget("user:{}:detail".format(reply.from_user_id), "avatar").decode(),
                'to_user_id': reply.to_user_id,
                'created_at': ct.convertDatetime(reply.created_at),
                'likes': redis.scard('bsreply:{}:likes'.format(reply.id)),
                'liked': redis.sismember('bsreply:{}:likes'.format(reply.id), request.user.username) if request.user.is_authenticated else False
            } for reply in replies]
        else:
            replies = []

        return JsonResponse({'code': 1, 'msg': replies})


class BlogReplyStore(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '请先登录再进行操作'})

        data = json.loads(request.body)
        blog_id = data['id']
        body = data['body'].strip()
        to_user_id = data['to_user_id']

        if len(body) < 1 or len(body) > 1000:
            return JsonResponse({'code': 3, 'msg': '回复内容有效长度区间为[1-300]'})

        if Blog.objects.filter(id=blog_id).count() is not 1:
            return JsonResponse({'code': 5, 'msg': '找不到该博客'})

        if User.objects.filter(username=to_user_id).count() is not 1:
            return JsonResponse({'code': 6, 'msg': '所回复用户不存在'})

        blog_reply = BlogReply.objects.create(
            blog_id=blog_id,
            body=body,
            from_user_id=request.user.username,
            to_user_id=to_user_id
        )

        redis = get_redis()
        ct = ConvertTime()

        blog_reply = {
            'id': blog_reply.id,
            'body': blog_reply.body,
            'from_user_id': blog_reply.from_user_id,
            'from_user_nickname': redis.hget("user:{}:detail".format(blog_reply.from_user_id), "nickname").decode(),
            'from_user_avatar': redis.hget("user:{}:detail".format(blog_reply.from_user_id), "avatar").decode(),
            'to_user_id': blog_reply.to_user_id,
            'created_at': ct.convertDatetime(blog_reply.created_at),
            'sub_replies_count': 0,
            'likes': 0,
            'liked': False

        }
        return JsonResponse({'code': 1, 'msg': blog_reply})


class BlogSubReplyStore(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '请先登录再进行操作'})

        data = json.loads(request.body)
        blog_id = data['id']
        reply_id = data['reply_id']
        to_reply = data['to_reply']
        body = data['body'].strip()
        to_user_id = data['to_user_id']

        if len(body) < 1 or len(body) > 1000:
            return JsonResponse({'code': 3, 'msg': '回复内容有效长度区间为[1-300]'})

        if Blog.objects.filter(id=blog_id).count() is not 1:
            return JsonResponse({'code': 5, 'msg': '找不到该博客'})

        if User.objects.filter(username=to_user_id).count() is not 1:
            return JsonResponse({'code': 6, 'msg': '所回复用户不存在'})

        sub_reply = BlogSubReply.objects.create(
            blog_id=blog_id,
            reply_id=reply_id,
            to_reply=to_reply,
            body=body,
            from_user_id=request.user.username,
            to_user_id=to_user_id
        )

        redis = get_redis()
        ct = ConvertTime()

        sub_reply = {
            'id': sub_reply.id,
            'reply_id': sub_reply.reply_id,
            'body': sub_reply.body,
            'from_user_id': sub_reply.from_user_id,
            'from_user_nickname': redis.hget("user:{}:detail".format(sub_reply.from_user_id), "nickname").decode(),
            'from_user_avatar': redis.hget("user:{}:detail".format(sub_reply.from_user_id), "avatar").decode(),
            'to_user_id': sub_reply.to_user_id,
            'created_at': ct.convertDatetime(sub_reply.created_at),
            'likes': 0,
            'liked': False
        }
        return JsonResponse({'code': 1, 'msg': sub_reply})


class BlogReplyDelete(View):
    def get(self, request, id):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '请先登录再进行操作'})
        level = request.GET['level']
        support_levels = ['reply', 'subreply']

        if level not in support_levels:
            return JsonResponse({'code': 5, 'msg': '参数错误'})

        reply = BlogReply.objects.filter(
            pk=id)[0] if level == 'reply' else BlogSubReply.objects.filter(pk=id)[0]
        if reply is None:
            return JsonResponse({'code': 2, 'msg': '找不到该评论'})
        from_user_id = reply.from_user_id
        if request.user.username != from_user_id:
            return JsonResponse({'code': 3, 'msg': '你无权删除'})

        redis = get_redis()

        if level == 'reply':
            for r in reply.sub_replies.all():
                redis.delete('bsreply:{}:likes'.format(r.id))
            redis.delete('breply:{}:likes'.format(reply.id))
        else:
            redis.delete('bsreply:{}:likes'.format(reply.id))

        reply.delete()

        return JsonResponse({'code': 1, 'msg': '删除成功'})


class BlogAndReplyLikes(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '请先登录再进行操作'})
        way = request.GET['way']
        identity = request.GET['id']
        addOrRem = request.GET['aor']

        redis = get_redis()
        support_ways = ['blog', 'breply', 'bsreply']
        if way not in support_ways:
            return JsonResponse({'code': 2, 'msg': '出错，找不到所给参数的有效集合'})

        key = way + ':' + identity + ':likes'
        if addOrRem == 'add':
            redis.sadd(key, request.user.username)
        if addOrRem == 'rem':
            redis.srem(key, request.user.username)
        return JsonResponse({'code': 1, 'msg': '操作成功'})
