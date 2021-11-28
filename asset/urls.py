from django.urls import path

from . import views

app_name = 'asset'

urlpatterns = [
    path('add/', views.AssetCreateView.as_view(), name='add'),
    path('list/', views.AssetListView.as_view(), name='list'),
    path('my_list/', views.MyAssetListView.as_view(), name='my_list'),
    path('my_pending_list/', views.MyPendingAssetListView.as_view(), name='my_pending_list'),
    path('edit/<int:pk>', views.AssetUpdateView.as_view(), name='update'),
]