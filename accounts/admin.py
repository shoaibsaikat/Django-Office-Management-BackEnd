from django.contrib import admin

from rest_framework.authtoken.admin import TokenAdmin

from .models import Profile

admin.site.register(Profile)

# django rest framework token management
TokenAdmin.raw_id_fields = ['user']
