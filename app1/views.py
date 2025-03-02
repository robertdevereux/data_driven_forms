import csv, json, bleach
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from urllib.parse import urlencode
from .models import Question, Routing, Section, Schedule, Regime, Permission

def upload_sections(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        reader = csv.reader(file.read().decode('utf-8').splitlines())
        next(reader)  # Skip header row

        for row in reader:
            section_id, section_name, schedule_ids = row[0], row[1], row[2]
            section, created = Section.objects.update_or_create(
                section_id=section_id,
                defaults={"section_name": section_name}
            )

            # Link the section to schedules
            for schedule_id in schedule_ids.split(';'):
                schedule = Schedule.objects.filter(schedule_id=schedule_id.strip()).first()
                if schedule:
                    section.schedules.add(schedule)

        messages.success(request, "Sections uploaded successfully!")
        return redirect('upload_sections')

    return render(request, 'app1/upload_csv.html', {'data_name':'Section'})


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

def upload_routing(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        reader = csv.reader(file.read().decode('utf-8').splitlines())
        next(reader)  # Skip header row

        for row in reader:
            section = get_object_or_404(Section, section_id=row[0])
            current_question = get_object_or_404(Question, question_id=row[1])
            next_question = get_object_or_404(Question, question_id=row[3]) if row[3] != "END" else None

            QuestionRouting.objects.update_or_create(
                section=section,
                current_question=current_question,
                answer_value=row[2] if row[2] else None,
                defaults={'next_question': next_question, 'end_process': (row[3] == "END")}
            )

        messages.success(request, "Routing uploaded successfully!")
        return redirect('upload_routing')

    return render(request, 'app1/upload_routing.html')

def display_questions(request):
    data = Question.objects.order_by('question_id').all()
    return render(request, 'app1/display_questions.html', {'dbtest_data': data})

def display_routing(request):
    data = QuestionRouting.objects.order_by('section', 'current_question').all()
    return render(request, 'app1/display_routing.html', {'dbtest_data': data})

def display_permissions(request):
    data = Permission.objects.order_by('user_id','regime_id','schedule_id','section_id').all()
    return render(request, 'app1/display_permissions.html', {'dbtest_data': data})

def display_regimes(request):
    data = Regime.objects.order_by('regime_id').all()
    return render(request, 'app1/display_regimes.html', {'dbtest_data': data})

def display_schedules(request):
    data = Section.objects.all()
    return render(request, 'app1/display_schedules.html', {'dbtest_data': data})

def display_sections(request):
    data = Section.objects.order_by('section_id').all()
    return render(request, 'app1/display_sections.html', {'dbtest_data': data})

def user_login(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id").strip()
        if not user_id:
            messages.error(request, "Please enter a valid user ID.")
            return redirect("user_login")

        request.session["user_id"] = user_id
        permissions = Permission.objects.filter(user_id=user_id)
        request.session["permissions"] = list(permissions.values())

        return redirect("select_regime")

    return render(request, "app1/user.html")


def select_regime(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("user_login")

    permissions = request.session.get("permissions", [])
    print(f"DEBUG: Permissions from session: {permissions}")  # Check session data

    regime_ids = {perm["regime_id"] for perm in permissions if perm.get("regime_id")}
    print(f"DEBUG: Extracted regime IDs: {regime_ids}")  # Check extracted IDs

    regimes = Regime.objects.filter(regime_id__in=regime_ids)
    print(f"DEBUG: Retrieved regimes: {[r.regime_name for r in regimes]}")  # Check query results

    if request.method == "POST":
        regime_id = request.POST.get("regime_id")
        if regime_id in regime_ids:
            request.session["regime_id"] = regime_id
            return redirect("select_schedule")
        messages.error(request, "Invalid regime selection.")

    return render(request, "app1/regime.html", {"regimes": regimes})


def select_schedule(request):
    return HttpResponse("Placeholder for selecting a schedule.")


def select_section(request):
    return HttpResponse("Placeholder for selecting a section.")


def question_router(request, question_id):
    return HttpResponse(f"Routing to question {question_id}.")


def radio_view(request, question_id):
    return HttpResponse(f"Displaying radio question {question_id}.")


def text_view(request, question_id):
    return HttpResponse(f"Displaying text question {question_id}.")


def checkbox_view(request, question_id):
    return HttpResponse(f"Displaying checkbox question {question_id}.")


def process_answer(request, question_id):
    return HttpResponse(f"Processing answer for {question_id}.")


def completion_page(request):
    return HttpResponse("Completion page placeholder.")


def restart_process(request):
    return HttpResponse("Restarting process.")