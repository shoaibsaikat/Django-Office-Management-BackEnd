from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User

import json

from .models import Profile

@csrf_exempt
def signin(request):
    if (request.method == 'POST'):
        user = None
        if (request.POST.get('username', False) and request.POST.get('password', False)):
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        else:
            return JsonResponse({'message': 'User not authenticated'}, status = 500)
        if (user is not None):
            login(request, user)
            return JsonResponse({'message': 'Login successful'}, status = 200)
        else:
            return JsonResponse({'message': 'User not found'}, status = 500)
    return JsonResponse({'message': 'Login failed'}, status = 500)

@login_required
def signout(request):
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'}, status = 200)

@login_required
@csrf_exempt
def change_password(request):
    if request.method == 'POST':
        if (request.POST.get('lastpassword', False) and request.POST.get('newpassword1', False) and request.POST.get('newpassword2', False)):
            currentPasswordEntered = request.POST['lastpassword']
            password1 = request.POST['newpassword1']
            password2 = request.POST['newpassword2']
            passwordMatched = check_password(currentPasswordEntered, request.user.password)
            if (passwordMatched and password1 == password2):
                #change password code
                user = request.user
                user.set_password(password1)
                user.save()
                update_session_auth_hash(request, user)  # Important!
                return JsonResponse({'message': 'Password successfully updated'}, status = 200)
            else:
                return JsonResponse({'message': 'Password mismatch'}, status = 500)
        else:
            return JsonResponse({'message': 'Password not changed'}, status = 500)
    return JsonResponse({'message': 'Invalid change request'}, status = 500)

@login_required
@csrf_exempt
def change_manager(request):
    if request.method == 'POST':
        # change manager
        if (request.POST.get('manager', False)):
            pk = request.POST['manager']
            manager = User.objects.get(pk=pk)
            profile = Profile.objects.get(pk=request.user.pk)
            profile.supervisor = manager
            profile.save()
            return JsonResponse({'message': 'User manager changed'}, status = 200)
        else:
            return JsonResponse({'message': 'Invalid manager'}, status = 500)
    elif request.method == 'GET':
        profiles = Profile.objects.all()
        profileJsons = [ob.as_json() for ob in profiles]
        return JsonResponse({'users': json.dumps(profileJsons)}, status = 200)
    return JsonResponse({'message': 'Invalid change request'}, status = 500)

@method_decorator(csrf_exempt, name='dispatch')
class ChangeInfoView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = {
           'first_name':  self.request.user.first_name,
           'last_name': self.request.user.last_name,
           'email': self.request.user.email
        }
        return JsonResponse({'user': json.dumps(user)}, status = 200)

    def post(self, request, *args, **kwargs):
        if (request.POST.get('first_name', False) and request.POST.get('last_name', False) and request.POST.get('email', False)):
            user = request.user
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.email = request.POST['email']
            user.save()
            return JsonResponse({'message': 'User info updated'}, status = 200)
        return JsonResponse({'message': 'User updated error'}, status = 500)
