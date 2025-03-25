# regime_uc/urls.py
from django.urls import path
from regime_dwp_uc.views import start
from . import views

urlpatterns = [
    path('', views.start, name='start'),
]