"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('app1.urls')),  # this sends http://127.0.0.1:8000 to app1 (and that sends '' to app1_home
    path('admin/', admin.site.urls), # this sends http://127.0.0.1:8000/admin off to admin site
    path('tester/', include('tester.urls')),  # this sends http://127.0.0.1:8000/tester off to tester (and that sends '' to tester_home
]
