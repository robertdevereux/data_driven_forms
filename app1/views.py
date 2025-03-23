import csv, json, bleach
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.contrib import messages
from urllib.parse import urlencode
from .models import Permission, Regime, Schedule, Section, Routing, Question

def completion_page(request):
    error_message = request.GET.get("error_message", "")  # Ensure error message is a string
    final_json = request.session.get("final_json")  # Retrieve stored JSON

    if not final_json:
        final_json = json.dumps({"message": "No responses recorded"}, indent=4)  # Default JSON if empty

    return render(request, "app1/completion.html", {
        "error_message": error_message,
        "final_json": final_json
    })

def restart_process(request):
    print("******** SESSION DATA BEFORE FLUSH ********")
    print(request.session.items())  # Prints all session key-value pairs
    request.session.clear()
    request.session.flush()
    request.session.create()  # Ensures a new session ID is generated

    print("******** SESSION DATA AFTER FLUSH ********")
    print(request.session.items())  # Prints all session key-value pairs

    return redirect("user_login")

def task_list(request):
    progress=[{'name':'Task 1', 'hint':'some hint', 'status':'Not started'}]
    return render(request, "app1/task_list.html", {"progress": progress})

def total(table_answers, column_names):
    # This routine sums the values of specified columns in a table
    # column_names needs to be a list of the identifiers for the selected column questions

    # FOR NOW create some test data in the format of table_answers
    table_answers = {1: {'A': 23, 'B': 300}, 2: {'A': 3, 'B': 40}, 5: {'A': 1000, 'B': 2000}}
    print('a is: ', a)
    names=['A','C']

    # set up variable names for running totals, and record count, as a list
    names_totals = []
    for key in a[1]:  # $$$ insert extra check here $$$
        name_original = str(key)
        name_total = name_original + '_total'
        names.append([name_original, name_total])

    # create new dictionay items
    a['Total'] = {}
    a['Total']['record_count'] = 0
    for name in names:
        a['Total'][name[1]] = 0

    # compute running totals and record count (note only one iteration however many fields to be summed)
    for i in iter(a):
        if i != 'Total':
            a['Total']['record_count'] += 1
            for name in names:
                a['Total'][name[1]] += a[i][name[0]]

    print('a is now: ', a)

