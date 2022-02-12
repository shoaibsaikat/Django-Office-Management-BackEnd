from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signin/', views.SignInView.as_view(), name='signin'),
    path('signout/', views.signout, name='signout'),
    path('chnage_password/', views.change_password, name='change_password'), # change password
    path('change_manager/', views.change_manager, name='change_manager'), # update manager
    path('change_profile/', views.ChangeInfoView.as_view(), name='change_info'), # update profile
]
