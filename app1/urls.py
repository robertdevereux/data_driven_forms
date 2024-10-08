from django.urls import path
from . import views

urlpatterns = [
    path('', views.app1_home),
    path('p2/', views.p2),
]