from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    path('get/', views.UserView.as_view(), name='get_user_info'),
    path('signout/', views.signout, name='signout'),
    path('change_password/', views.change_password, name='change_password'), # change password
    path('change_manager/', views.change_manager, name='change_manager'), # update manager
    path('change_profile/', views.ChangeInfoView.as_view(), name='change_info'), # update profile
]
