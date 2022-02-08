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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.parsers import JSONParser
from rest_framework import status

import json

from .models import Profile

class SignInView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        user = None
        if (request.POST.get('username', False) and request.POST.get('password', False)):
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        else:
            return JsonResponse({'detail': 'No credential sent'}, status=400)
        if (user is not None):
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            userDict = user.profile.as_json()
            userDict['token'] = token.key
            return JsonResponse(userDict, status=status.HTTP_200_OK)
            # status is optional
        else:
            return JsonResponse({'detail': 'User not authenticated'}, status=400)
            # NOTE: by returning status 200 we can get the message in Angular frontend.
            # If 400 is returned then the bad request is handled by Angualr's internal library and message is not sent to UI

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signout(request):
    if request.method == 'POST':
        # print('got header: ' + str(request.headers))
        request.user.auth_token.delete()
        return JsonResponse({'detail': 'User signed out'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
                return JsonResponse({'detail': 'Password successfully updated'}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({'detail': 'Password mismatch'}, status=400)
        else:
            return JsonResponse({'detail': 'Password not changed'}, status=400)
    return JsonResponse({'detail': 'Invalid change request'}, status=400)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def change_manager(request):
    if request.method == 'POST':
        # change manager
        if (request.POST.get('manager', False)):
            pk = request.POST['manager']
            manager = User.objects.get(pk=pk)
            profile = Profile.objects.get(pk=request.user.pk)
            profile.supervisor = manager
            profile.save()
            return JsonResponse({'detail': 'User manager changed'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'detail': 'Invalid manager'}, status=400)
    elif request.method == 'GET':
        profiles = Profile.objects.all()
        profileJsons = [ob.as_json() for ob in profiles]
        return JsonResponse({'user_list': json.dumps(profileJsons)}, status=status.HTTP_200_OK)
    return JsonResponse({'detail': 'Invalid change request'}, status=400)

class ChangeInfoView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        user = request.user
        user.first_name = request.data['first_name']
        user.last_name = request.data['last_name']
        user.email = request.data['email']
        user.save()
        return JsonResponse({'detail': 'User info updated'}, status=status.HTTP_200_OK)
