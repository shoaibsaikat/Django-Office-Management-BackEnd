from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User

from datetime import datetime

from . import forms
from . import models

import json
import logging
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

class InventoryListView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        inventoryList = models.Inventory.objects.all()
        # pagination
        page = request.GET.get('page', 1)
        inventories = get_paginated_date(page, inventoryList, PAGE_COUNT)
        inventoryJsons = [ob.as_json() for ob in inventories]
        return JsonResponse({'inventory_list': json.dumps(inventoryJsons)}, status = 200)

    def test_func(self):
        return self.request.user.profile.canDistributeInventory or self.request.user.profile.canApproveInventory

@method_decorator(csrf_exempt, name='dispatch')
class InventoryCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, *args, **kwargs):
        if (request.POST.get('name', False) and request.POST.get('description', False) and request.POST.get('unit', False) and
            request.POST.get('count', False)):
            inventory = models.Inventory()
            inventory.name = request.POST['name']
            inventory.description = request.POST['description']
            inventory.unit = request.POST['unit']
            inventory.count = int(request.POST['count'])
            inventory.save()
        else:
            return JsonResponse({'message': 'Inventory creation failed'}, status = 400)
        return redirect('inventory:list')

    def test_func(self):
        return self.request.user.profile.canDistributeInventory or self.request.user.profile.canApproveInventory

@method_decorator(csrf_exempt, name='dispatch')
class InventoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        inventory = models.Inventory.objects.get(pk=kwargs['pk'])
        return JsonResponse({'inventory': json.dumps(inventory.as_json())}, status = 200)

    def post(self, request, *args, **kwargs):
        if (request.POST.get('description', False) and request.POST.get('unit', False) and request.POST.get('count', False)):
            inventory = models.Inventory.objects.get(pk=kwargs['pk'])
            inventory.description = request.POST['description']
            inventory.unit = request.POST['unit']
            inventory.count = request.POST['count']
            inventory.save()
        else:
            return JsonResponse({'message': 'Inventory update failed'}, status = 400)
        return JsonResponse({'message': 'Inventory updated'}, status = 200)

    def test_func(self):
        return self.request.user.profile.canDistributeInventory or self.request.user.profile.canApproveInventory

@method_decorator(csrf_exempt, name='dispatch')
class RequisitionCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        inventories = models.Inventory.objects.all()
        inventoryJsons = [ob.as_json() for ob in inventories]
        # generating approver list for dropdown
        users = User.objects.all()
        profiles = []
        for user in users:
            profiles.append(user.profile)
        profileJsons = [ob.as_json() for ob in profiles]
        return JsonResponse({'inventory_list': json.dumps(inventoryJsons), 'approver_list': json.dumps(profileJsons)}, status = 200)

    def post(self, request, *args, **kwargs):
        if (request.POST.get('title', False) and request.POST.get('inventory', False) and request.POST.get('approver', False) and
            request.POST.get('amount', False) and request.POST.get('comment', False)):
            requisition = models.Requisition()
            requisition.title = request.POST['title']
            requisition.approver = models.User.objects.get(pk=int(request.POST['approver']))
            requisition.inventory = models.Inventory.objects.get(pk=int(request.POST['inventory']))
            requisition.amount = int(request.POST['amount'])
            requisition.comment = request.POST['comment']
            requisition.save()
        else:
            return JsonResponse({'message': 'Requisition creation failed'}, status = 400)
        return redirect('inventory:my_requisition')

class MyRequisitionListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        requisitionList = models.Requisition.objects.filter(user=self.request.user).order_by('-pk')
        # pagination
        page = request.GET.get('page', 1)
        requisitions = get_paginated_date(page, requisitionList, PAGE_COUNT)
        requisitionJsons = [ob.as_json() for ob in requisitions]
        return JsonResponse({'requisition_list': json.dumps(requisitionJsons)}, status = 200)

@method_decorator(csrf_exempt, name='dispatch')
class RequisitionListView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        requisitionList = models.Requisition.objects.filter(approver=self.request.user, approved=False).order_by('-pk')
        # pagination
        page = request.GET.get('page', 1)
        requisitions = get_paginated_date(page, requisitionList, PAGE_COUNT)
        requisitionJsons = [ob.as_json() for ob in requisitions]

        # generating distributor list for dropdown
        users = User.objects.all()
        profiles = []
        for user in users:
            profiles.append(user.profile)
        profileJsons = [ob.as_json() for ob in profiles]
        return JsonResponse({'requisition_list': json.dumps(requisitionJsons), 'distributor_list': json.dumps(profileJsons)}, status = 200)

    def post(self, request, *args, **kwargs):
        requisition = models.Requisition.objects.filter(pk=request.POST['pk']).first()
        requisition.approved = True

        if (request.POST.get('distributor', False)):
            requisition.distributor = models.User.objects.filter(pk=request.POST['distributor']).first()
            requisition.approveDate = datetime.now()
            requisition.save()
        return redirect('inventory:requisition_list')

    def test_func(self):
        return self.request.user.profile.canApproveInventory

@method_decorator(csrf_exempt, name='dispatch')
class RequisitionDetailFormView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        requisition = models.Requisition.objects.filter(pk=kwargs['pk'], approver=self.request.user, approved=False).first()
        # generating distributor list for dropdown
        users = User.objects.all()
        profiles = []
        for user in users:
            profiles.append(user.profile)
        profileJsons = [ob.as_json() for ob in profiles]
        return JsonResponse({
            'requisition': json.dumps(None if requisition is None else requisition.as_json()),
            'distributor_list': json.dumps(profileJsons)},
            status = 200)

    def post(self, request, *args, **kwargs):
        requisition = models.Requisition.objects.get(pk=kwargs['pk'])
        requisition.approved = True
        if (request.POST.get('distributor', False)):
            requisition.distributor = models.User.objects.filter(pk=request.POST['distributor']).first()
            requisition.approveDate = datetime.now()
            requisition.save()
        return redirect('inventory:requisition_list')

    def test_func(self):
        return self.request.user.profile.canDistributeInventory or self.request.user.profile.canApproveInventory

class RequisitionDetailView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        requisition = models.Requisition.objects.get(pk=kwargs['pk'])
        return JsonResponse({'requisition': json.dumps(requisition.as_json())}, status = 200)

    def test_func(self):
        return self.request.user.profile.canDistributeInventory or self.request.user.profile.canApproveInventory

class RequisitionApprovedListView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        requisitionList = models.Requisition.objects.filter(distributor=self.request.user, distributed=False).order_by('-pk')
        # pagination
        page = request.GET.get('page', 1)
        requisitions = get_paginated_date(page, requisitionList, PAGE_COUNT)
        requisitionJsons = [ob.as_json() for ob in requisitions]
        return JsonResponse({'requisition_list': json.dumps(requisitionJsons)}, status = 200)

    def test_func(self):
        return self.request.user.profile.canDistributeInventory

class RequisitionHistoryList(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        requisitionList = models.Requisition.objects.all().order_by('-requestDate', '-pk')
        # pagination
        page = request.GET.get('page', 1)
        requisitions = get_paginated_date(page, requisitionList, PAGE_COUNT)
        requisitionJsons = [ob.as_json() for ob in requisitions]
        return JsonResponse({'requisition_list': json.dumps(requisitionJsons)}, status = 200)

    def test_func(self):
        return self.request.user.profile.canDistributeInventory or self.request.user.profile.canApproveInventory

@csrf_protect
@login_required
@user_passes_test(lambda u: u.profile.canDistributeInventory)
@transaction.atomic
def requisitionDistribution(request, pk):
    requisition = models.Requisition.objects.filter(pk=pk).first()
    inventory = models.Inventory.objects.filter(pk=requisition.inventory.pk).first()
    if (inventory.count < requisition.amount):
        return JsonResponse({'message': 'Distribution failed! Inventory low, please add items to the inventory first'}, status = 400)
    else:
        requisition.distributed = True
        requisition.distributionDate = datetime.now()
        inventory.count = inventory.count - requisition.amount 
        requisition.save()
        inventory.save()
    return redirect('inventory:requisition_approved_list')

@csrf_protect
@login_required
@user_passes_test(lambda u: u.profile.canDistributeInventory or u.profile.canApproveInventory)
def inventoryQuickEdit(request, pk, amount):
    item = models.Inventory.objects.get(pk=pk)
    item.count = amount
    item.save()
    return redirect('inventory:list')

def getInventoryList(request):
    if (request.is_ajax and request.method == 'GET'):
        list = models.Inventory.objects.all()
        return JsonResponse({'inventory_list': serializers.serialize('json', list)}, status = 200)
    return JsonResponse({}, status = 400)
