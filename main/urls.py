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
from django.conf.urls.static import static
from django.conf import settings
import os


urlpatterns = [

    path('', include('core_home.urls')),  # root path goes to core_home

    path('regime-dwp-uc/', include(('regime_dwp_uc.urls', 'regime_dwp_uc'), namespace='regime_dwp_uc')),
    path('regime-dwp-fg/', include(('regime_dwp_fg.urls', 'regime_dwp_fg'), namespace='regime_dwp_fg')),
    path('regime-hmrc-iht/', include(('regime_hmrc_iht.urls','regime_hmrc_iht'), namespace='regime_hmrc_iht')),

    path('app1/', include('app1.urls')),  # This makes sure all app1 views are prefixed
    path('admin/', admin.site.urls), # this sends http://127.0.0.1:8000/admin off to admin site
    path('tester/', include('tester.urls')),  # this sends http://127.0.0.1:8000/tester off to tester app (and that sends '' to tester_home
] + static('/assets/', document_root=os.path.join(settings.BASE_DIR, 'app1/static/assets'))
