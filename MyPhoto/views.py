import time
import os
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from .models import Photo
from MyHome.utils import get_uuid_base64, ConvertTime
from django.core import exceptions
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from qiniu import Auth as qiniu_auth
from qiniu import put_file, etag, BucketManager, CdnManager
import qiniu.config

# Create your views here.


class PhotoGet(View):
    def get(self, request, id):
        key = "photo:{}:info".format(id)
        photo = cache.get(key)
        if photo is None:
            print('---')
            try:
                photo = Photo.objects.get(pk=id)

                ct = ConvertTime()

                photo = {
                    'id': photo.id,
                    'url': photo.url,
                    'title': photo.title,
                    'caption': photo.caption,
                    'created_at': ct.convertDatetime(photo.created_at)
                }
                cache.set(key, photo, 30)
            except exceptions.ObjectDoesNotExist:
                return JsonResponse({'code': 2, 'msg': '找不到该图片'})
        return JsonResponse({'code': 1, 'msg': photo})


class PhotoSet(View):
    def get(self, request, username):
        photo_set = Photo.objects.filter(
            author_id=username).order_by('-created_at')
        if photo_set:
            photos = [{
                'id': photo.id,
                'url': '{}-thumbnail'.format(photo.url)
            } for photo in photo_set]

            # blog_set = json.loads(serializers.serialize('json', blog_set))
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
