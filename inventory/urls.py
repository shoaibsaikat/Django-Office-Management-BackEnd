from django.urls import path

from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.InventoryListView.as_view(), name='list'),
    path('create/', views.InventoryCreateView.as_view(), name='create'),
    path('edit/<int:pk>/', views.InventoryUpdateView.as_view(), name='edit'),
    path('quick_edit/', views.inventoryQuickEdit, name='quick_edit'),
    path('requisition/create/', views.RequisitionCreateView.as_view(), name='create_requisition'),
    path('requisition/my_list/', views.MyRequisitionListView.as_view(), name='my_requisition'),
    path('requisition/detail/<int:pk>/', views.RequisitionDetailView.as_view(), name='requisition_detail'),
    path('requisition/approval/', views.RequisitionApprovalListView.as_view(), name='approval_list'),
    path('requisition/distribution/', views.RequisitionDistributionListView.as_view(), name='distribution_list'),
    path('requisition/history/', views.RequisitionHistoryList.as_view(), name='requisition_history'),
    # for chart
    path('inventory_list/', views.getInventoryListForChart, name='inventory_list'), 
]
