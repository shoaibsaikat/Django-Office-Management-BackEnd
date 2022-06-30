from lib2to3.pgen2 import driver
from django.http import JsonResponse
from django.http import JsonResponse
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework import status

from datetime import datetime

from accounts.models import Profile
from .models import Route, RouteUser

import json

PAGE_COUNT = 10

class DriverUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        if (request.user.profile.canManageDriver is False):
            return JsonResponse({'detail': 'Permission denied.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        driver = Profile.objects.get(user__pk=kwargs['pk'])
        if driver is not None:
            driver.phone1 = request.data['phone1']
            phone2 = request.data['phone2']
            if phone2 != '':
                driver.phone2 = request.data['phone2']
            image = request.data['image']
            if image != '':
                driver.image = request.data['image']
            driver.save()
            return JsonResponse({'detail': 'Driver info updated.'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'detail': 'Invalid driver.'}, status=status.HTTP_404_NOT_FOUND)

class DriverListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if (request.user.profile.canManageDriver is False):
            return JsonResponse({'detail': 'Permission denied.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        driverList = Profile.objects.filter(type=3)
        # pagination
        page = int(request.GET.get('page', 1))
        listCount = len(driverList)
        driverList = driverList[(page - 1) * PAGE_COUNT : ((page - 1) * PAGE_COUNT) + PAGE_COUNT]
        # json
        driverJsons = [ob.as_json() for ob in driverList]
        return JsonResponse({'driver_list': json.dumps(driverJsons), 'count': listCount}, status=status.HTTP_200_OK)
