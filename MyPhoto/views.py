import time
import os
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.contrib.auth.models import User

from .models import Photo, PhotoReply, PhotoSubReply
from MyHome.utils import get_redis, get_uuid_base64, ConvertTime
from django.core import exceptions
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from qiniu import Auth as qiniu_auth
from qiniu import put_file, etag, BucketManager, CdnManager
import qiniu.config

# Create your views here.


class PhotoGet(View):
    def get(self, request, id):
        # key = "photo:{}:info".format(id)
        # photo = cache.get(key)
        # if photo is None:
        try:
            photo = Photo.objects.get(pk=id)

            redis = get_redis()
            ct = ConvertTime()

            photo = {
                'id': photo.id,
                'author_id': photo.author_id,
                'url': photo.url,
                'title': photo.title,
                'caption': photo.caption,
                'author': redis.hget("user:{}:detail".format(photo.author_id), "nickname").decode(),
                'author_avatar': redis.hget("user:{}:detail".format(photo.author_id), "avatar").decode(),
                'created_at': ct.convertDatetime(photo.created_at),
                'replies_count': photo.replies.count() + photo.sub_replies.count(),
                'likes': redis.scard("photo:{}:likes".format(photo.id)),
                'liked': redis.sismember("photo:{}:likes".format(photo.id), request.user.username) if request.user.is_authenticated else False
            }
            return JsonResponse({'code': 1, 'msg': photo})
            # cache.set(key, photo, 120)
        except exceptions.ObjectDoesNotExist:
            return JsonResponse({'code': 2, 'msg': '找不到该图片'})


class PhotoSet(View):
    def get(self, request, username):
        photo_set = Photo.objects.filter(
            author_id=username).order_by('-created_at')
        if photo_set:
            photos = [{
                'id': photo.id,
                'url': '{}-thumbnail'.format(photo.url)
            } for photo in photo_set]

            return JsonResponse({'code': 1, 'msg': photos})
        return JsonResponse({'code': 2, 'msg': '未找到相关图片'})


class PhotoStore(View):
    def post(self, request):
        # 判断是否已经登陆
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '上传图片请先登录'})
        data = json.loads(request.body)
        url = data['photoUrl'].strip()
        title = data['title'].strip()
        caption = data['caption'].strip()

        if len(url) is 0:
            return JsonResponse({'code': 2, 'msg': '图片不能为空'})
        if len(title) > 50:
            return JsonResponse({'code': 2, 'msg': '标题不能超过50个字符'})
        if len(caption) is 0 or len(caption) > 500:
            return JsonResponse({'code': 2, 'msg': '图片说明不能为空且不超过500个字符'})

        photo = Photo.objects.create(
            id=get_uuid_base64(),
            url=url,
            title=title,
            caption=caption,
            author_id=request.user.username
        )
        return JsonResponse({'code': 1, 'msg': {'id': photo.id, 'url': '{}-thumbnail'.format(photo.url)}})


class PhotoUpload(View):
    def post(self, request):
        # 判断是否已经登陆
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '上传图片请先登录'})

        photo = request.FILES.get('photo')
        if not photo:
            return JsonResponse({'code': 2, 'msg': '请选择需要上传的图片'})

        allow_types = ['image/jpeg', 'image/png', 'image/gif']

        if photo.content_type not in allow_types:
            return JsonResponse({'code': 3, 'msg': '上传失败，文件类型错误'})

        file_name = '{}_photo_{}_{}'.format(
            request.user.username, time.time(), photo.name)

        fs = FileSystemStorage()
        fs.save(file_name, photo)
        file_path = os.path.join(
            os.getcwd(), 'media', file_name).replace('\\', '/')

        access_key = 'M2TrolxfManTFNP4Clr3M12JW0tvAaCV0xIbrZk5'
        secret_key = 'Llh0byt0KDHwiFlcNVvPiTpQSrH8IrZSt5puu1zS'

        q = qiniu_auth(access_key, secret_key)
        bucket_name = 'photo'

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
            used_photo = request.GET['used_photo']
            if used_photo:
                try:
                    bucket = BucketManager(q)
                    key = os.path.basename(used_photo)
                    ret, info = bucket.delete(bucket_name, key)
                    assert ret == {}
                except Exception as e:
                    pass

            # 更新图片地址
            url = 'http://pkuk9xor9.bkt.clouddn.com/{}'.format(file_name)

            # 刷新缓存
            cdn_manager = CdnManager(q)
            urls = [url]
            cdn_manager.refresh_urls(urls)

            return JsonResponse({'code': 1, 'msg': url})


class PhotoAndReplyLikes(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '请先登录再进行操作'})
        way = request.GET['way']
        identity = request.GET['id']
        addOrRem = request.GET['aor']

        redis = get_redis()

        support_ways = ['photo', 'preply', 'psreply']
        if way not in support_ways:
            return JsonResponse({'code': 2, 'msg': '参数错误'})

        key = way + ':' + identity + ':likes'
        if addOrRem == 'add':
            redis.sadd(key, request.user.username)
        if addOrRem == 'rem':
            redis.srem(key, request.user.username)
        return JsonResponse({'code': 1, 'msg': '操作成功'})


class PhotoReplyGet(View):
    def get(self, request):
        photo_id = request.GET['id']
        replies = PhotoReply.objects.filter(
            photo_id=photo_id)[:10]
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
                'likes': redis.scard('preply:{}:likes'.format(reply.id)),
                'liked': redis.sismember('preply:{}:likes'.format(reply.id), request.user.username) if request.user.is_authenticated else False
            } for reply in replies]
        else:
            replies = []

        return JsonResponse({'code': 1, 'msg': replies})


class PhotoSubReplyGet(View):
    def get(self, request):
        reply_id = request.GET['id']
        replies = PhotoSubReply.objects.filter(
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
                'likes': redis.scard('psreply:{}:likes'.format(reply.id)),
                'liked': redis.sismember('psreply:{}:likes'.format(reply.id), request.user.username) if request.user.is_authenticated else False
            } for reply in replies]
        else:
            replies = []

        return JsonResponse({'code': 1, 'msg': replies})


class PhotoReplyStore(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '请先登录再进行操作'})

        data = json.loads(request.body)
        photo_id = data['id']
        body = data['body'].strip()
        to_user_id = data['to_user_id']

        if len(body) < 1 or len(body) > 1000:
            return JsonResponse({'code': 3, 'msg': '回复内容有效长度区间为[1-300]'})

        if Photo.objects.filter(id=photo_id).count() is not 1:
            return JsonResponse({'code': 5, 'msg': '找不到该图片'})

        if User.objects.filter(username=to_user_id).count() is not 1:
            return JsonResponse({'code': 6, 'msg': '所回复用户不存在'})

        photo_reply = PhotoReply.objects.create(
            photo_id=photo_id,
            body=body,
            from_user_id=request.user.username,
            to_user_id=to_user_id
        )

        redis = get_redis()
        ct = ConvertTime()

        photo_reply = {
            'id': photo_reply.id,
            'body': photo_reply.body,
            'from_user_id': photo_reply.from_user_id,
            'from_user_nickname': redis.hget("user:{}:detail".format(photo_reply.from_user_id), "nickname").decode(),
            'from_user_avatar': redis.hget("user:{}:detail".format(photo_reply.from_user_id), "avatar").decode(),
            'to_user_id': photo_reply.to_user_id,
            'created_at': ct.convertDatetime(photo_reply.created_at),
            'sub_replies_count': 0,
            'likes': 0,
            'liked': False
        }
        return JsonResponse({'code': 1, 'msg': photo_reply})


class PhotoSubReplyStore(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '请先登录再进行操作'})

        data = json.loads(request.body)
        photo_id = data['id']
        reply_id = data['reply_id']
        to_reply = data['to_reply']
        body = data['body'].strip()
        to_user_id = data['to_user_id']

        if len(body) < 1 or len(body) > 1000:
            return JsonResponse({'code': 3, 'msg': '回复内容有效长度区间为[1-300]'})

        if Photo.objects.filter(id=photo_id).count() is not 1:
            return JsonResponse({'code': 5, 'msg': '找不到该博客'})

        if User.objects.filter(username=to_user_id).count() is not 1:
            return JsonResponse({'code': 6, 'msg': '所回复用户不存在'})

        sub_reply = PhotoSubReply.objects.create(
            photo_id=photo_id,
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


class PhotoReplyDelete(View):
    def get(self, request, id):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 4, 'msg': '请先登录再进行操作'})
        level = request.GET['level']
        support_levels = ['reply', 'subreply']

        if level not in support_levels:
            return JsonResponse({'code': 5, 'msg': '参数错误'})

        reply = PhotoReply.objects.filter(
            pk=id)[0] if level == 'reply' else PhotoSubReply.objects.filter(pk=id)[0]
        if reply is None:
            return JsonResponse({'code': 2, 'msg': '找不到该评论'})
        from_user_id = reply.from_user_id
        if request.user.username != from_user_id:
            return JsonResponse({'code': 3, 'msg': '你无权删除'})

        redis = get_redis()

        if level == 'reply':
            for r in reply.sub_replies.all():
                redis.delete('psreply:{}:likes'.format(r.id))
            redis.delete('preply:{}:likes'.format(reply.id))
        else:
            redis.delete('psreply:{}:likes'.format(reply.id))

        reply.delete()

        return JsonResponse({'code': 1, 'msg': '删除成功'})
