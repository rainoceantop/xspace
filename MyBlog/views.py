from django.http import HttpResponse, JsonResponse
from django.views import View
from .models import Blog, BlogReply
from django.contrib.auth.models import User
from django.core import serializers, exceptions
from django.core.files.storage import FileSystemStorage
from django.core.cache import cache
from django_redis import get_redis_connection
from django.db.models import Q, F
from MyHome.utils import ConvertTime, get_redis

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
            # 获取回复
            replies = blog.replies.all()
            if replies:
                replies = [{
                    'id': reply.id,
                    'to_reply': reply.to_reply,
                    'parent_reply': reply.parent_reply,
                    'body': reply.body,
                    'from_user_id': reply.from_user_id,
                    'from_user_nickname': redis.hget("user:{}:detail".format(reply.from_user_id), "nickname").decode(),
                    'from_user_avatar': redis.hget("user:{}:detail".format(reply.from_user_id), "avatar").decode(),
                    'to_user_id': reply.to_user_id,
                    'created_at': ct.convertDatetime(reply.created_at),
                    'likes': redis.scard('reply:{}:likes'.format(reply.id)),
                    'liked': redis.sismember('reply:{}:likes'.format(reply.id), request.user.id) if request.user.is_authenticated else False
                } for reply in replies]
            else:
                replies = ['']

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
                'replies_count': blog.replies.count(),
                'likes': redis.scard('blog:{}:likes'.format(blog.id)),
                'liked': redis.sismember('blog:{}:likes'.format(blog.id), request.user.id) if request.user.is_authenticated else False
            }

            return JsonResponse({'code': 1, 'msg': blog, 'addition': replies})
        except exceptions.ObjectDoesNotExist:
            return JsonResponse({'code': 2, 'msg': '找不到该博客'})


# 获取blog set
class BlogSet(View):
    def get(self, request, uid):
        blog_set = Blog.objects.filter(
            author_id=uid).order_by('-created_at')
        if blog_set:
            blogs = [{
                'id': blog.id,
                'title': blog.title
            } for blog in blog_set]

            # blog_set = json.loads(serializers.serialize('json', blog_set))
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
            title=title,
            body=body,
            author_id=request.user.id
        )
        return JsonResponse({'code': 1, 'msg': blog.id})


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
            if blog.author_id is request.user.id:
                blog.title = title
                blog.body = body
                blog.save()
                return JsonResponse({'code': 1, 'msg': blog.id})
            return JsonResponse({'code': 8, 'msg': '修改失败，你无权修改别人的博客'})
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
            if blog.author_id is request.user.id:
                # 获取该博客的所有评论id
                delete_ids = []
                for r in blog.replies.all():
                    delete_ids.append(r.id)
                # 删除博客点赞
                redis.delete('blog:{}:likes'.format(id))
                # 删除评论点赞
                for i in delete_ids:
                    redis.delete('reply:{}:likes'.format(i))

                # 删除博客
                blog.delete()
                return JsonResponse({'code': 1, 'msg': '删除成功'})
            return JsonResponse({'code': 3, 'msg': '删除失败，你无权删除别人的博客'})
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
        bucket_name = 'blog'

        try:
            token = q.upload_token(bucket_name, file_name, 3600)
            ret, info = put_file(token, file_name, file_path)
            assert ret['key'] == file_name
            assert ret['hash'] == etag(file_path)
        except Exception as e:
            return JsonResponse({'uploaded': False, 'msg': '上传文件出错'})
        finally:
            fs.delete(file_name)
            return JsonResponse({'uploaded': True, 'url': 'http://pjk94dt0u.bkt.clouddn.com/{}'.format(file_name)})


class BlogReplyStore(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '请先登录再进行操作'})

        data = json.loads(request.body)
        blog_id = data['blog_id']
        to_reply = data['to_reply']
        parent_reply = data['parent_reply']
        body = data['body'].strip()
        to_user_id = data['to_user_id']

        if len(body) < 1 or len(body) > 1000:
            return JsonResponse({'code': 3, 'msg': '回复内容有效长度区间为[1-300]'})

        if Blog.objects.filter(id=blog_id).count() is not 1:
            return JsonResponse({'code': 5, 'msg': '找不到该博客'})

        if User.objects.filter(id=to_user_id).count() is not 1:
            return JsonResponse({'code': 6, 'msg': '所回复用户不存在'})

        blog_reply = BlogReply.objects.create(
            blog_id=blog_id,
            to_reply=to_reply,
            parent_reply=parent_reply,
            body=body,
            from_user_id=request.user.id,
            to_user_id=to_user_id
        )

        redis = get_redis()
        ct = ConvertTime()

        blog_reply = {
            'id': blog_reply.id,
            'to_reply': blog_reply.to_reply,
            'parent_reply': blog_reply.parent_reply,
            'body': blog_reply.body,
            'from_user_id': blog_reply.from_user_id,
            'from_user_nickname': redis.hget("user:{}:detail".format(blog_reply.from_user_id), "nickname").decode(),
            'from_user_avatar': redis.hget("user:{}:detail".format(blog_reply.from_user_id), "avatar").decode(),
            'to_user_id': blog_reply.to_user_id,
            'created_at': ct.convertDatetime(blog_reply.created_at),
            'likes': redis.scard('reply:{}:likes'.format(blog_reply.id)),
            'liked': redis.sismember('reply:{}:likes'.format(blog_reply.id), request.user.id)

        }
        return JsonResponse({'code': 1, 'msg': blog_reply})


class BlogReplyDelete(View):
    def get(self, request, id):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '请先登录再进行操作'})
        reply = BlogReply.objects.filter(pk=id)[0]
        if reply is None:
            return JsonResponse({'code': 2, 'msg': '找不到该评论'})
        from_user_id = reply.from_user_id
        parent_id = reply.parent_reply
        if request.user.id is not from_user_id:
            return JsonResponse({'code': 3, 'msg': '你无权删除'})

        delete_ids = []
        delete_ids.append(reply.id)

        if parent_id is 0:
            for r in BlogReply.objects.filter(parent_reply=reply.id):
                delete_ids.append(r.id)
                r.delete()
        reply.delete()

        redis = get_redis()
        for id in delete_ids:
            redis.delete('reply:{}:likes'.format(id))
        return JsonResponse({'code': 1, 'msg': '删除成功'})


class BlogAndReplyLikes(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '请先登录再进行操作'})
        way = request.GET['way']
        identity = request.GET['id']
        addOrRem = request.GET['aor']

        redis = get_redis()
        if way != 'blog' and way != 'reply':
            return JsonResponse({'code': 2, 'msg': '出错，找不到所给参数的有效集合'})
        if not identity.isdigit():
            return JsonResponse({'code': 3, 'msg': '出错，找不到所给参数的有效集合'})

        key = way + ':' + identity + ':likes'
        if addOrRem == 'add':
            redis.sadd(key, request.user.id)
        if addOrRem == 'rem':
            redis.srem(key, request.user.id)
        return JsonResponse({'code': 1, 'msg': '操作成功'})
