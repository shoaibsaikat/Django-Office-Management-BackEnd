from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic.edit import FormView
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import json

from .forms import SigninForm, ProfileForm, InfoForm
from .models import Profile

@csrf_exempt
def signin(request):
    if request.method == 'POST':
        user = None
        if request.POST.get('username', False) and request.POST.get('password', False):
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return HttpResponse('Login Successful')
    return HttpResponse('Login Page')

@login_required
def signout(request):
    logout(request)
    # return redirect('index')
    return HttpResponse('Successfully logged out!')

# TODO:
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })

# TODO:
@login_required
def change_manager(request):
    profile = Profile.objects.get(pk=request.user.pk)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile.save()
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/change_supervisor.html', {
        'form': form
    })

@method_decorator(csrf_exempt, name='dispatch')
class ChangeInfoView(LoginRequiredMixin, FormView):
    # template_name = 'accounts/edit_profile.html'
    # form_class = InfoForm
    # success_url = reverse_lazy('accounts:change_info')

    def get(self, request, *args, **kwargs):
        user = {
           'first_name':  self.request.user.first_name,
           'last_name': self.request.user.last_name,
           'email': self.request.user.email
        }
        # return JsonResponse(json.loads(json.dumps(user)))
        return JsonResponse({'user': json.dumps(user)}, status = 200)

    def post(self, request, *args, **kwargs):
        user = request.user
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.email = request.POST['email']
        user.save()
        # messages.success(request, 'User info updated!')
        return HttpResponse('Changed successfully!')
