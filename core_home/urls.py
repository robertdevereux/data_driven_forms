# core_home/urls.py
from django.urls import path

from core_home.views import consistency_check, user_login, select_regime

urlpatterns = [
    path('', consistency_check, name='home'),
    path('user_login/', user_login, name='user_login'),
    path('select_regime/', select_regime, name='select_regime'),
]
