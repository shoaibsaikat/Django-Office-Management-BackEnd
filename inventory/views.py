from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User

from datetime import datetime

from time import mktime

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

class InventoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    login_url = '/user/signin/'
    redirect_field_name = 'redirect_to'

    model = models.Inventory
    fields = ['name', 'description', 'unit', 'count']
    success_url = reverse_lazy('inventory:list')

    def test_func(self):
        return self.request.user.profile.canDistributeInventory or self.request.user.profile.canApproveInventory

class InventoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):

    def get(self, request, *args, **kwargs):
        inventory = models.Inventory.objects.get(pk=kwargs['pk'])
        return render(request, 'inventory/inventory_update_form.html', {'form': inventory})

    def post(self, request, *args, **kwargs):
        inventory = models.Inventory.objects.get(pk=kwargs['pk'])
        inventory.description = self.request.POST['description']
        inventory.unit = self.request.POST['unit']
        inventory.count = self.request.POST['count']
        inventory.save()
        messages.success(request, "Information updated!")
        return render(request, 'inventory/inventory_update_form.html', {'form': inventory})

    def test_func(self):
        return self.request.user.profile.canDistributeInventory or self.request.user.profile.canApproveInventory

class RequisitionCreateView(LoginRequiredMixin, CreateView):
    model = models.Requisition
    form_class = forms.RequisitionForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

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

        if request.POST.get('distributor', False):
            requisition.distributor = models.User.objects.filter(pk=request.POST['distributor']).first()
            requisition.approveDate = datetime.now()
            requisition.save()
        return redirect('inventory:requisition_list')

    def test_func(self):
        return self.request.user.profile.canApproveInventory

class RequisitionDetailFormView(LoginRequiredMixin, UserPassesTestMixin, View):

    def get(self, request, *args, **kwargs):
        requisition = models.Requisition.objects.filter(pk=kwargs['pk'], approver=self.request.user, approved=False).first()
        users = models.User.objects.all()
        return render(request, 'inventory/requisition_detail_form.html', {'requisition': requisition, 'users': users})

    def post(self, request, *args, **kwargs):
        # logger.warning('distributor: {}'.format(request.POST['distributor']))
        requisition = models.Requisition.objects.filter(pk=kwargs['pk']).first()
        requisition.approved = True
        if request.POST.get('distributor', False):
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
    # ordering = ['-requestDate']
    def get(self, request, *args, **kwargs):
        requisitionList = models.Requisition.objects.all().order_by('-pk')
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
    if inventory.count < requisition.amount:
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
    # messages.success(request, item.name + ' updated!')
    return redirect('inventory:list')

def getInventoryList(request):
    if request.is_ajax and request.method == 'GET':
        list = models.Inventory.objects.all()
        return JsonResponse({'inventory_list': serializers.serialize('json', list)}, status = 200)
    return JsonResponse({}, status = 400)
