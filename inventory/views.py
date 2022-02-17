from django.http import JsonResponse
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.http import JsonResponse
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework import status

from datetime import datetime

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

class InventoryListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, *args, **kwargs):
        if (request.user.profile.canDistributeInventory is False and request.user.profile.canApproveInventory is False):
            return JsonResponse({'detail': 'Permission denied.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        inventoryList = models.Inventory.objects.all()
        # pagination
        page = request.GET.get('page', 1)
        inventories = get_paginated_date(page, inventoryList, PAGE_COUNT)
        inventoryJsons = [ob.as_json() for ob in inventories]
        return JsonResponse({'inventory_list': json.dumps(inventoryJsons)}, status=status.HTTP_200_OK)

class InventoryCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        inventory = models.Inventory()
        inventory.name = request.data['name']
        inventory.description = request.data['description']
        inventory.unit = request.data['unit']
        inventory.count = int(request.data['count'])
        inventory.save()
        return JsonResponse({}, status=status.HTTP_200_OK)

    # def test_func(self):
    #     return self.request.user.profile.canDistributeInventory or self.request.user.profile.canApproveInventory

class InventoryUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, *args, **kwargs):
        inventory = models.Inventory.objects.get(pk=kwargs['pk'])
        return JsonResponse({'inventory': json.dumps(inventory.as_json())}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        inventory = models.Inventory.objects.get(pk=kwargs['pk'])
        inventory.description = request.data['description']
        inventory.unit = request.data['unit']
        inventory.count = request.data['count']
        inventory.save()
        return JsonResponse({'detail': 'Inventory updated.'}, status=status.HTTP_200_OK)

    # def test_func(self):
    #     return self.request.user.profile.canDistributeInventory or self.request.user.profile.canApproveInventory

class RequisitionCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, *args, **kwargs):
        inventories = models.Inventory.objects.all()
        inventoryJsons = [ob.as_json() for ob in inventories]
        # generating approver list for dropdown
        users = User.objects.all()
        profiles = []
        for user in users:
            profiles.append(user.profile)
        profileJsons = [ob.as_json() for ob in profiles]
        return JsonResponse({'inventory_list': json.dumps(inventoryJsons), 'approver_list': json.dumps(profileJsons)}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        requisition = models.Requisition()
        requisition.title = request.data['title']
        requisition.approver = models.User.objects.get(pk=int(request.data['approver']))
        requisition.inventory = models.Inventory.objects.get(pk=int(request.data['inventory']))
        requisition.amount = int(request.data['amount'])
        requisition.comment = request.data['comment']
        requisition.save()
        return JsonResponse({}, status=status.HTTP_200_OK)

class MyRequisitionListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, *args, **kwargs):
        requisitionList = models.Requisition.objects.filter(user=self.request.user).order_by('-pk')
        # pagination
        page = request.GET.get('page', 1)
        requisitions = get_paginated_date(page, requisitionList, PAGE_COUNT)
        requisitionJsons = [ob.as_json() for ob in requisitions]
        return JsonResponse({'requisition_list': json.dumps(requisitionJsons)}, status=status.HTTP_200_OK)

class RequisitionListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

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
        return JsonResponse({'requisition_list': json.dumps(requisitionJsons), 'distributor_list': json.dumps(profileJsons)}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        requisition = models.Requisition.objects.filter(pk=request.data['pk']).first()
        requisition.approved = True

        requisition.distributor = models.User.objects.filter(pk=request.data['distributor']).first()
        requisition.approveDate = datetime.now()
        requisition.save()
        return JsonResponse({}, status=status.HTTP_200_OK)

    # def test_func(self):
    #     return self.request.user.profile.canApproveInventory

class RequisitionDetailFormView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

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
            status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        requisition = models.Requisition.objects.get(pk=kwargs['pk'])
        requisition.approved = True
        requisition.distributor = models.User.objects.filter(pk=request.data['distributor']).first()
        requisition.approveDate = datetime.now()
        requisition.save()
        return JsonResponse({}, status=status.HTTP_200_OK)

    # def test_func(self):
    #     return self.request.user.profile.canDistributeInventory or self.request.user.profile.canApproveInventory

class RequisitionDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, *args, **kwargs):
        requisition = models.Requisition.objects.get(pk=kwargs['pk'])
        return JsonResponse({'requisition': json.dumps(requisition.as_json())}, status=status.HTTP_200_OK)

    # def test_func(self):
    #     return self.request.user.profile.canDistributeInventory or self.request.user.profile.canApproveInventory

class RequisitionApprovedListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, *args, **kwargs):
        requisitionList = models.Requisition.objects.filter(distributor=self.request.user, distributed=False).order_by('-pk')
        # pagination
        page = request.GET.get('page', 1)
        requisitions = get_paginated_date(page, requisitionList, PAGE_COUNT)
        requisitionJsons = [ob.as_json() for ob in requisitions]
        return JsonResponse({'requisition_list': json.dumps(requisitionJsons)}, status=status.HTTP_200_OK)

    # def test_func(self):
    #     return self.request.user.profile.canDistributeInventory

class RequisitionHistoryList(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, *args, **kwargs):
        requisitionList = models.Requisition.objects.all().order_by('-requestDate', '-pk')
        # pagination
        page = request.GET.get('page', 1)
        requisitions = get_paginated_date(page, requisitionList, PAGE_COUNT)
        requisitionJsons = [ob.as_json() for ob in requisitions]
        return JsonResponse({'requisition_list': json.dumps(requisitionJsons)}, status=status.HTTP_200_OK)

    # def test_func(self):
    #     return self.request.user.profile.canDistributeInventory or self.request.user.profile.canApproveInventory

# @user_passes_test(lambda u: u.profile.canDistributeInventory)
@transaction.atomic
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def requisitionDistribution(request, pk):
    requisition = models.Requisition.objects.filter(pk=pk).first()
    inventory = models.Inventory.objects.filter(pk=requisition.inventory.pk).first()
    if (inventory.count < requisition.amount):
        return JsonResponse({'detail': 'Distribution failed! Inventory low, please add items to the inventory first.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        requisition.distributed = True
        requisition.distributionDate = datetime.now()
        inventory.count = inventory.count - requisition.amount 
        requisition.save()
        inventory.save()
    return JsonResponse({}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def inventoryQuickEdit(request):
    if (request.user.profile.canDistributeInventory is False and request.user.profile.canApproveInventory is False):
        return JsonResponse({'detail': 'Permission denied.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    item = models.Inventory.objects.get(pk=request.data['pk'])
    item.count = request.data['amount']
    item.save()
    return JsonResponse({'detail': 'Amount updated.'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@parser_classes([JSONParser])
def getInventoryList(request):
    if (request.is_ajax and request.method == 'GET'):
        list = models.Inventory.objects.all()
        return JsonResponse({'inventory_list': serializers.serialize('json', list)}, status=status.HTTP_200_OK)
    return JsonResponse({}, status=status.HTTP_406_NOT_ACCEPTABLE)
