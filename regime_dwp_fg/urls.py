from django.urls import path
from . import views

app_name = "regime_dwp_fg"

urlpatterns = [
    path('', views.start, name='start'),
]
