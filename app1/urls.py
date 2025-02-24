from django.urls import path
from .views import upload_screen_questions, upload_screen_routing
from . import views

urlpatterns = [
    path('', views.app1_home),
    path('p2/', views.p2),
    path('upload/questions/', upload_screen_questions, name='upload_screen_questions'),
    path('upload/routing/', upload_screen_routing, name='upload_screen_routing'),
]