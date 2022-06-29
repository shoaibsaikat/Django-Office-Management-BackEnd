from django.urls import path

from . import views

app_name = 'driver'

urlpatterns = [
    path('list/', views.DriverListView.as_view(), name='list'),
    path('edit/<int:pk>/', views.DriverUpdateView.as_view(), name='edit'),
]
