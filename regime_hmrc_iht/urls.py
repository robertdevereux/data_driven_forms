from django.urls import path
from . import views

urlpatterns = [
    path('', views.start, name='start'),  # Or name it more precisely if needed
]
