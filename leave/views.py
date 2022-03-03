from itertools import count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
from django.http import JsonResponse

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework import status

from datetime import datetime, date

from .models import Leave

import json

PAGE_COUNT = 10

YEAR_CHOICE = (
    (date.today().year, date.today().year),
    (date.today().year - 1, date.today().year - 1),
    (date.today().year - 2, date.today().year - 2),
)

def get_paginated_date(page, list, count):
    paginator = Paginator(list, count)
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)
    return pages

class LeaveCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, *args, **kwargs):
        if self.request.user.profile.supervisor is None:
            return JsonResponse({'detail': 'Add manager first'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return JsonResponse({'detail': 'Ok'}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        leave = Leave()
        leave.user = self.request.user
        leave.approver = self.request.user.profile.supervisor
        leave.title = request.data['title']
        leave.startDate = datetime.strptime(request.data['start'], '%Y-%m-%d')
        leave.endDate = datetime.strptime(request.data['end'], '%Y-%m-%d')
        leave.dayCount = int(request.data['days'])
        leave.comment = request.data['comment']
        leave.save()
        return JsonResponse({'detail': 'Leave created'}, status=status.HTTP_200_OK)

# my leaves
class LeaveMyListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, *args, **kwargs):
        leaveList = Leave.objects.filter(user=self.request.user).order_by('-pk')
        # pagination
        page = request.GET.get('page', 1)
        leaves = get_paginated_date(page, leaveList, PAGE_COUNT)
        leaveJsons = [ob.as_json() for ob in leaves]
        return JsonResponse({'leave_list': json.dumps(leaveJsons)}, status=status.HTTP_200_OK)

# leaves requested to me
class LeaveRequestListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, *args, **kwargs):
        if (request.user.profile.canApproveLeave is False):
            return JsonResponse({'detail': 'Permission denied.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        leaveList = Leave.objects.filter(approver=self.request.user, approved=False).order_by('-pk')
        # pagination
        page = request.GET.get('page', 1)
        leaves = get_paginated_date(page, leaveList, PAGE_COUNT)
        leaveJsons = [ob.as_json() for ob in leaves]
        return JsonResponse({'leave_list': json.dumps(leaveJsons)}, status=status.HTTP_200_OK)

class LeaveDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, *args, **kwargs):
        if (request.user.profile.canApproveLeave is False):
            return JsonResponse({'detail': 'Permission denied.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        detail = Leave.objects.get(pk=kwargs['pk'])
        return JsonResponse({'detail': json.dumps(detail.as_json())}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        if (request.user.profile.canApproveLeave is False):
            return JsonResponse({'detail': 'Permission denied.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        leave = Leave.objects.get(pk=kwargs['pk'])
        leave.approveDate = datetime.now()
        leave.approved = True
        leave.save()
        return JsonResponse({'detail': 'Leave approved.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def leaveApprove(request, pk):
    leave = Leave.objects.get(pk=pk)
    leave.approveDate = datetime.now()
    leave.approved = True
    leave.save()
    return JsonResponse({'detail': 'Leave approved.'}, status=status.HTTP_200_OK)

class LeaveSummaryListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, *args, **kwargs):
        if (request.user.profile.canApproveLeave is False):
            return JsonResponse({'detail': 'Permission denied.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        page = int(request.GET.get('page', 1))
        # print('got page: ' + str(page))
        year = kwargs['year']
        # returning custom dictionary
        leaveList = Leave.objects.filter(approved=True, startDate__gte=date(year, 1, 1), startDate__lte=date(year, 12, 31)) \
                        .values('user', 'user__first_name', 'user__last_name') \
                        .annotate(days=Sum('dayCount'))
        listCount = len(leaveList)
        leaveList = leaveList[(page - 1) * PAGE_COUNT : ((page - 1) * PAGE_COUNT) + PAGE_COUNT]
        # make custom dictionary list from queryset
        leaveDictionaryList = []
        for leave in leaveList:
            leaveDictionaryList.append({
                'user': leave.get('user'),
                'first_name': leave.get('user__first_name'),
                'last_name': leave.get('user__last_name'),
                'days': leave.get('days'),
            })

        # for index in range(len(leaveDictionaryList)):
        #     for key in leaveDictionaryList[index]:
        #         print(leaveDictionaryList[index][key])

        return JsonResponse({'leave_list': json.dumps(leaveDictionaryList), 'count': listCount}, status=status.HTTP_200_OK)
