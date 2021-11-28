from django.http.response import HttpResponse
from django.shortcuts import render

def IndexPage(request):
    return render(request, 'index.html')
