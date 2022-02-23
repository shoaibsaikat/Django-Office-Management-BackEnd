from django.urls import path

from . import views

app_name = 'leave'

urlpatterns = [
    path('create/', views.LeaveCreateView.as_view(), name='create'),
    path('my_list/', views.LeaveMyListView.as_view(), name='my_list'),
    path('request_list/', views.LeaveRequestListView.as_view(), name='request_list'),
    path('request/approve/<int:pk>/', views.leaveApprove, name='leave_approve'),
    path('detail/<int:pk>/', views.LeaveDetailView.as_view(), name='detail'),
    path('summary/<int:year>/', views.LeaveSummaryListView.as_view(), name='summary'),
]
