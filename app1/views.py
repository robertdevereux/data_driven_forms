from django.shortcuts import render
from django.http import HttpResponse

def app1_home(request):
    return HttpResponse("This is the home page of the app app1")

def p2(request):
    return HttpResponse("This is the 2nd page of the app app1")

