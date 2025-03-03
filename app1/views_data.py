import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Regime, Schedule,Section,Routing, Question, Permission

def upload_regimes(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        reader = csv.reader(file.read().decode('utf-8').splitlines())
        next(reader)  # Skip header row
        for row in reader:
            p=Regime(regime_id=row[0],regime_name=row[1])
            p.save()
        messages.success(request, "Regimes uploaded successfully!")
        return redirect('upload_regimes')

    return render(request, 'app1/upload_csv.html', {'data_name':'Regime'})

def upload_schedules(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        reader = csv.reader(file.read().decode('utf-8').splitlines())
        next(reader)  # Skip header row
        for row in reader:
            p=Schedule(regime_id=row[0],schedule_id=row[1],schedule_name=row[2])
            p.save()
        messages.success(request, "Schedules uploaded successfully!")
        return redirect('upload_schedules')

    return render(request, 'app1/upload_csv.html', {'data_name':'Schedule'})

def upload_sections(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        reader = csv.reader(file.read().decode('utf-8').splitlines())
        next(reader)  # Skip header row
        for row in reader:
            p=Section(schedule_id=row[0],section_id=row[1],section_name=row[2])
            p.save()
        messages.success(request, "Sections uploaded successfully!")
        return redirect('upload_sections')

    return render(request, 'app1/upload_csv.html', {'data_name':'Section'})

def upload_routing(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        reader = csv.reader(file.read().decode('utf-8').splitlines())
        next(reader)  # Skip header row
        for row in reader:
            p=Routing(section_id=row[0],current_question=row[1],answer_value=row[2],next_question=row[3])
            p.save()
        messages.success(request, "Routing uploaded successfully!")
        return redirect('upload_routing')

    return render(request, 'app1/upload_csv.html', {'data_name':'Routing'})

def upload_questions(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        reader = csv.reader(file.read().decode('utf-8').splitlines())
        next(reader)  # Skip header row

        for row in reader:
            Question.objects.update_or_create(
                question_id=row[0],
                defaults={
                    'question_type': row[1],
                    'guidance': row[2],
                    'question_text': row[3],
                    'hint': row[4],
                    'answer_type': row[5],
                    'options': row[6],
                    'parent_question_id': row[7] if row[7] else None
                }
            )

        messages.success(request, "Questions uploaded successfully!")
        return redirect('upload_questions')

    return render(request, 'app1/upload_questions.html')

def upload_permissions(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        reader = csv.reader(file.read().decode('utf-8').splitlines())
        next(reader)  # Skip header row
        for row in reader:
            p=Permission(user_id=row[0],regime_id=row[1],schedule_id=row[2],section_id=row[3])
            p.save()
        messages.success(request, "Permissions uploaded successfully!")
        return redirect('upload_permissions')

    return render(request, 'app1/upload_csv.html', {'data_name':'Permission'})

def display_regimes(request):
    data = Regime.objects.order_by('regime_id').all()
    return render(request, 'app1/display_regimes.html', {'dbtest_data': data})

def display_schedules(request):
    data = Schedule.objects.order_by('regime_id','schedule_id').all()
    return render(request, 'app1/display_schedules.html', {'dbtest_data': data})

def display_sections(request):
    data = Section.objects.order_by('schedule_id','section_id').all()
    return render(request, 'app1/display_sections.html', {'dbtest_data': data})

def display_routing(request):
    data = Routing.objects.order_by('section_id', 'current_question','answer_value').all()
    return render(request, 'app1/display_routing.html', {'dbtest_data': data})

def display_questions(request):
    data = Question.objects.order_by('question_id').all()
    return render(request, 'app1/display_questions.html', {'dbtest_data': data})

def display_permissions(request):
    data = Permission.objects.order_by('user_id','regime_id','schedule_id','section_id').all()
    return render(request, 'app1/display_permissions.html', {'dbtest_data': data})



