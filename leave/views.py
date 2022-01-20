from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views import View
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core import serializers

from datetime import datetime, date

from . import forms
from .models import Leave

from time import mktime
import datetime

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

class LeaveCreateView(LoginRequiredMixin, CreateView):
    model = Leave
    form_class = forms.LeaveForm
    success_url = reverse_lazy('leave:my_list')
    
    def get(self, request, *args, **kwargs):
        if self.request.user.profile.supervisor is None:
            messages.error(request, 'Add your manager first')
            return redirect('accounts:change_manager')
        return render(request, 'leave/leave_form.html', {'form': forms.LeaveForm()})

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.approver = self.request.user.profile.supervisor
        return super().form_valid(form)

# my leaves
class LeaveListView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        leaveList = Leave.objects.filter(user=self.request.user).order_by('-pk')
        # pagination
        page = request.GET.get('page', 1)
        leaves = get_paginated_date(page, leaveList, PAGE_COUNT)
        return render(request, 'leave/leave_list.html', {'object_list': leaves})

# leaves requested to me
class LeaveRequestListView(LoginRequiredMixin, UserPassesTestMixin, View):

    def get(self, request, *args, **kwargs):
        leaveList = Leave.objects.filter(approver=self.request.user, approved=False).order_by('-pk')
        # pagination
        page = request.GET.get('page', 1)
        leaves = get_paginated_date(page, leaveList, PAGE_COUNT)
        return render(request, 'leave/leave_approval_list.html', {'object_list': leaves})

    def test_func(self):
        return self.request.user.profile.canApproveLeave

class LeaveDetailView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        detail = Leave.objects.get(pk=kwargs['pk'])
        return render(request, 'leave/leave_detail.html', {'object': detail})

    def post(self, request, *args, **kwargs):
        leave = Leave.objects.get(pk=kwargs['pk'])
        leave.approveDate = datetime.now()
        leave.approved = True
        leave.save()
        return redirect('leave:request_list')

    def test_func(self):
        return self.request.user.profile.canApproveLeave

@login_required
@user_passes_test(lambda u: u.profile.canApproveLeave)
def leaveApprove(request, pk):
    leave = Leave.objects.get(pk=pk)
    leave.approveDate = datetime.now()
    leave.approved = True
    leave.save()
    return redirect('leave:request_list')

# class LeaveHistoryListView(LoginRequiredMixin, UserPassesTestMixin, View):

#     def get(self, request, *args, **kwargs):
#         year = date.today().year
#         leaveList = Leave.objects.filter(approved=True, startDate__gte=date(year, 1, 1), startDate__lte=date(year, 12, 31)).order_by('-pk')
#         # pagination
#         page = request.GET.get('page', 1)
#         leaves = get_paginated_date(page, leaveList, PAGE_COUNT)
#         return render(request, 'leave/leave_history.html', {'object_list': leaves})

#     def test_func(self):
#         return self.request.user.profile.canApproveLeave

class LeaveSummaryListView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        year = kwargs['year']
        leaveList = Leave.objects.filter(approved=True, startDate__gte=date(year, 1, 1), startDate__lte=date(year, 12, 31)) \
                        .values('user', 'user__first_name', 'user__last_name') \
                        .annotate(days=Sum('dayCount'))
        # pagination
        page = request.GET.get('page', 1)
        leaves = get_paginated_date(page, leaveList, PAGE_COUNT)
        leaveCustomlist = []
        print('-------' + str(leaves))
        for i in leaves:
            item = {
                'user_full_name': i.user__first_name + ' ' + i.user__last_name,
                'days': i.days,
            }
            leaveCustomlist.append(item)
        # leaveJsons = [ob.as_json() for ob in leaveList]
        return JsonResponse({'leave_list': json.dumps(leaveCustomlist), 'year_list': json.dumps(YEAR_CHOICE), 'selected_year': year}, status = 200)

    def test_func(self):
        return self.request.user.profile.canApproveLeave
