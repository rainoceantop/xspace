from django.http import JsonResponse
from django.db.models import Count
from django.views import View
from .models import Tag


class SearchTags(View):
    def get(self, request):
        searchText = request.GET['beginWith']
        tags = []
        if len(searchText) is not 0:
            tags = [{'id': tag.id, 'name': tag.name, 'post_count': tag.post_count} for tag in Tag.objects.annotate(post_count=Count('photos', distinct=True) + Count('blogs', distinct=True)).filter(
                name__startswith=searchText).order_by('-post_count')[:50]]
        return JsonResponse({'code': 1, 'msg': tags})
