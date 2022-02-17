from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes, parser_classes
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
            return JsonResponse({'detail': 'No credential sent'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if (user is not None):
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            userDict = user.profile.as_json()
            userDict['token'] = token.key
            return JsonResponse(userDict, status=status.HTTP_200_OK)
            # status is optional
        else:
            return JsonResponse({'detail': 'User not authenticated'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            # NOTE: by returning status 200 we can get the message in Angular frontend.
            # If 400 is returned then the bad request is handled by Angualr's internal library and message is not sent to UI

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def signout(request):
    if request.method == 'POST':
        # print('got header: ' + str(request.headers))
        request.user.auth_token.delete()
        return JsonResponse({'detail': 'User signed out'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def change_password(request):
    if request.method == 'POST':
        if (request.data['lastpassword'] and request.data['newpassword']):
            currentPasswordEntered = request.data['lastpassword']
            password = request.data['newpassword']
            passwordMatched = check_password(currentPasswordEntered, request.user.password)
            if (passwordMatched):
                #change password code
                user = request.user
                user.set_password(password)
                user.save()
                update_session_auth_hash(request, user)  # Important!
                return JsonResponse({'detail': 'Password successfully updated'}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({'detail': 'Wrong current password'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return JsonResponse({'detail': 'Password not changed'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    return JsonResponse({'detail': 'Invalid change request'}, status=status.HTTP_406_NOT_ACCEPTABLE)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def change_manager(request):
    if request.method == 'POST':
        # change manager
        if (request.data['manager']):
            pk = request.data['manager']
            manager = User.objects.get(pk=pk)
            profile = Profile.objects.get(pk=request.user.pk)
            profile.supervisor = manager
            profile.save()
            return JsonResponse({'detail': 'Manager changed'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'detail': 'Invalid manager'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    elif request.method == 'GET':
        profiles = Profile.objects.all()
        profileJsons = [ob.as_json() for ob in profiles]
        return JsonResponse({'user_list': json.dumps(profileJsons)}, status=status.HTTP_200_OK)
    return JsonResponse({'detail': 'Invalid change request'}, status=status.HTTP_406_NOT_ACCEPTABLE)

class ChangeInfoView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        user = request.user
        user.first_name = request.data['first_name']
        user.last_name = request.data['last_name']
        user.email = request.data['email']
        user.save()
        return JsonResponse({'detail': 'User info updated'}, status=status.HTTP_200_OK)
