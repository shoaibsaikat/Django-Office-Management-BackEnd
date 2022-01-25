from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Asset, AssetHistory, STATUS_CHOICE, TYPE_CHOICE

from time import mktime
import datetime

import json

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

PAGE_COUNT = 10

def get_paginated_date(page, list, count):
    paginator = Paginator(list, count)
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)
    return pages

@method_decorator(csrf_exempt, name='dispatch')
class AssetCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({'status': json.dumps(STATUS_CHOICE), 'type': json.dumps(TYPE_CHOICE)}, status = 200)

    def post(self, request, *args, **kwargs):
        if (request.POST.get('name', False) and request.POST.get('model', False) and request.POST.get('serial', False) and
            request.POST.get('purchaseDate', False) and request.POST.get('warranty', False) and request.POST.get('type', False) and
            request.POST.get('status', False) and request.POST.get('description', False)):

            user = request.user
            item = Asset()
            item.name = request.POST['name']
            item.model = request.POST['model']
            item.serial = request.POST['serial']
            item.purchaseDate = datetime.datetime.fromtimestamp(int(request.POST['purchaseDate']))
            item.warranty = int(request.POST['warranty'])
            item.type = int(request.POST['type'])
            item.status = int(request.POST['status'])
            item.description = request.POST['description']
            item.user = user
            item.save()

            # saving history
            history = AssetHistory()
            history.fromUser = self.request.user
            history.toUser = self.request.user
            history.asset = item
            history.save()
            return JsonResponse({'message': 'Asset created'}, status = 200)
        return JsonResponse({'message': 'Asset creation failed'}, status = 400)

    def test_func(self):
        return self.request.user.profile.canManageAsset

class AssetListView(LoginRequiredMixin, UserPassesTestMixin, View):
    paginate_by = PAGE_COUNT
    ordering = ['-purchaseDate']

    def get(self, request, *args, **kwargs):
        assets = Asset.objects.all()
        assetJsons = [ob.as_json() for ob in assets]
        return JsonResponse({'asset_list': json.dumps(assetJsons)}, status = 200)

    def test_func(self):
        return self.request.user.profile.canManageAsset

@method_decorator(csrf_exempt, name='dispatch')
class MyAssetListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        assetList = Asset.objects.filter(user=self.request.user)
        # calculating warranty last date
        for i in assetList:
            i.purchaseDate = i.purchaseDate + datetime.timedelta(days=i.warranty)

        # pagination
        page = request.GET.get('page', 1)
        assets = get_paginated_date(page, assetList, PAGE_COUNT)
        assetJsons = [ob.as_json() for ob in assets]

        users = User.objects.all()
        profiles = []
        for user in users:
            profiles.append(user.profile)
        profileJsons = [ob.as_json() for ob in profiles]

        # getting user list for dropdown
        users = User.objects.all()
        return JsonResponse({'asset_list': json.dumps(assetJsons), 'user_list': json.dumps(profileJsons)}, status = 200)

    def post(self, request, *args, **kwargs):
        if (request.POST.get('pk', False)):
            asset = Asset.objects.get(pk=request.POST['pk'])
            # logger.warning('assignee: {}'.format(request.POST['pk']))
            if request.POST.get('assignee', False):
                asset.next_user = User.objects.get(pk=request.POST['assignee'])
                asset.save()
            return redirect('asset:my_list')
        else:
            return JsonResponse({'message': 'Asset assign failed'}, status = 400)

@method_decorator(csrf_exempt, name='dispatch')
class MyPendingAssetListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        assetList = Asset.objects.filter(next_user=self.request.user)
        # calculating warranty last date
        for i in assetList:
            i.purchaseDate = i.purchaseDate + datetime.timedelta(days=i.warranty)

        # pagination
        page = request.GET.get('page', 1)
        assets = get_paginated_date(page, assetList, PAGE_COUNT)
        assetJsons = [ob.as_json() for ob in assets]

        return JsonResponse({'asset_list': json.dumps(assetJsons)}, status = 200)

    def post(self, request, *args, **kwargs):
        if (request.POST.get('pk', False)):
            asset = Asset.objects.get(pk=request.POST['pk'])

            # saving history
            history = AssetHistory()
            history.fromUser = asset.user
            history.toUser = self.request.user
            history.asset = asset
            history.save()

            # saving asset
            asset.user = self.request.user
            asset.next_user = None
            asset.save()

            return redirect('asset:my_pending_list')
        else:
            return JsonResponse({'message': 'Asset assign failed'}, status = 400)

@method_decorator(csrf_exempt, name='dispatch')
class AssetUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        asset = Asset.objects.get(pk=kwargs['pk'])
        return JsonResponse({'asset': json.dumps(asset.as_json()), 'status': json.dumps(STATUS_CHOICE), 'type': json.dumps(TYPE_CHOICE)}, status = 200)

    def post(self, request, *args, **kwargs):
        if (request.POST.get('name', False) and request.POST.get('model', False) and request.POST.get('serial', False) and
            request.POST.get('purchaseDate', False) and request.POST.get('warranty', False) and request.POST.get('type', False) and
            request.POST.get('status', False) and request.POST.get('description', False)):

            item = Asset.objects.get(pk=kwargs['pk'])
            item.name = request.POST['name']
            item.model = request.POST['model']
            item.serial = request.POST['serial']
            item.purchaseDate = datetime.datetime.fromtimestamp(int(request.POST['purchaseDate']))
            item.warranty = int(request.POST['warranty'])
            item.type = int(request.POST['type'])
            item.status = int(request.POST['status'])
            item.description = request.POST['description']
            item.save()
            return JsonResponse({'message': 'Asset updated'}, status = 200)
        return JsonResponse({'message': 'Asset update failed'}, status = 400)

    def test_func(self):
        return self.request.user.profile.canManageAsset
