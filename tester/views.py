from django.shortcuts import render
from django.http import HttpResponse
from django.db import connections
from django.db.utils import OperationalError
from .models import DBTest


def tester_home(request):
    return HttpResponse("This is the home page of the app tester")

def p2(request):
    return HttpResponse("This is the second page of the app tester")

def check_db_connection(request):
    db_conn = connections['default']
    try:
        db_conn.cursor()
        return HttpResponse("Database connection successful!")
    except OperationalError:
        return HttpResponse("Database connection failed!")

def display_dbtest_data(request):
    # Query all rows from the DBTest table
    dbtest_data = DBTest.objects.all()

    # Pass the data to the template
    return render(request, 'tester/display_data.html', {'dbtest_data': dbtest_data})
