# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.tester_home),
    path('p2/', views.p2),
    path('check-db/', views.check_db_connection, name='check_db_connection'),
    path('display/', views.display_dbtest_data, name='display_dbtest_data'),
    #path(‘new2’, views.new2, name = "template1"), illustration of using {% url ... %} HTML tag
    #path('displayCourse/<courseName>',  views.displayCourse),  illustration of passing 1 var
    #path('scoreCard/<courseName>/<hole>', views.scoreCard),  illustration of passing 2 vars
]