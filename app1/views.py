import csv
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import ScreenQuestion, ScreenRouting


def upload_screen_questions(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        file_path = file.temporary_file_path() if hasattr(file, 'temporary_file_path') else None

        if file_path:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
        else:
            reader = csv.reader(file.read().decode('utf-8').splitlines())

        next(reader)  # Skip header row

        for row in reader:
            ScreenQuestion.objects.update_or_create(
                id=row[0],
                defaults={
                    'question_type': row[1],
                    'guidance': row[2],
                    'question_text': row[3],
                    'hint': row[4],
                    'answer_type': row[5],
                    'options': row[6],
                    'parent_screen_id': row[7] if row[7] else None
                }
            )

        messages.success(request, "Screen Questions uploaded successfully!")
        return redirect('upload_screen_questions')

    return render(request, 'app1/upload_screen_questions.html')


def upload_screen_routing(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        file_path = file.temporary_file_path() if hasattr(file, 'temporary_file_path') else None

        if file_path:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
        else:
            reader = csv.reader(file.read().decode('utf-8').splitlines())

        next(reader)  # Skip header row

        for row in reader:
            ScreenRouting.objects.update_or_create(
                service_id=row[0],
                current_id=row[1],
                answer_value=row[2] if row[2] else None,
                defaults={'next_id': row[3]}
            )

        messages.success(request, "Screen Routing uploaded successfully!")
        return redirect('upload_screen_routing')

    return render(request, 'app1/upload_screen_routing.html')

def display_screen_questions(request):
    # Query all rows from the ScreenQuestion object
    data = ScreenQuestion.objects.all()

    # Pass the data to the template
    return render(request, 'app1/display_screen_questions.html', {'dbtest_data': data})

def display_screen_routing(request):
    # Query all rows from the DBTest table
    data = ScreenRouting.objects.all()

    # Pass the data to the template
    return render(request, 'app1/display_screen_routing.html', {'dbtest_data': data})


def app1_home(request):
    return HttpResponse("This is the home page of the app app1")

def p2(request):
    return HttpResponse("This is the 2nd page of the app app1")



