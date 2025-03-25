import csv, re

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Regime, Schedule,Section,Routing, Question, Permission, AnswerBasic, AnswerTable
from .forms import RegimeForm, ScheduleForm, SectionForm  # We'll create these forms

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
            p=Section(schedule_id=row[0],section_id=row[1],section_name=row[2], section_type=0)
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

        # Decode file and ensure correct parsing with quoted fields
        reader = csv.reader(file.read().decode('utf-8', errors='ignore').splitlines(), quotechar='"')
        next(reader)  # Skip header row
        for row in reader:
            row = (row + [None] * 8)[:8]  # Ensure row has at least 8 columns
            row = [re.sub(r'[\x00-\x1F\x7F-\x9F]', '', value).strip() if value else None for value in row]
            mapped_data = {
                'guidance': row[1] if row[1] else None,
                'question_text': row[2],
                'hint': row[3] if row[3] else None,
                'question_type': row[4],
                'options': row[5] if row[5] else None,
                'answer_type': row[6],  # Double-checking if row[6] is correct
                'parent_question_id': row[7] if row[7] else None
            }
            try:
                Question.objects.update_or_create(question_id=row[0], defaults=mapped_data)
            except:
                print(mapped_data)

        messages.success(request, "Questions uploaded successfully! Any errors printed in console")
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

def new_regime(request):
    """ View to create a new regime """
    if request.method == "POST":
        form = RegimeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New regime created successfully!")
            return redirect("new_regime")  # Redirect to the same page after success
    else:
        form = RegimeForm()

    return render(request, "app1/new_regime.html", {"form": form})

def new_schedule(request):
    """ View to create a new schedule """
    if request.method == "POST":
        form = ScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New schedule created successfully!")
            return redirect("new_schedule")
    else:
        form = ScheduleForm()

    return render(request, "app1/new_schedule.html", {"form": form})

def new_section(request):
    """ View to create a new section """
    if request.method == "POST":
        form = SectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New section created successfully!")
            return redirect("new_section")
    else:
        form = SectionForm()

    return render(request, "app1/new_section.html", {"form": form})

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
    data = Permission.objects.order_by('user_id','section_id').all()
    return render(request, 'app1/display_permissions.html', {'dbtest_data': data})

def display_answer_basic(request):
    data = AnswerBasic.objects.order_by('user_id','regime_id','question_id','answer','created_at').all()
    return render(request, 'app1/display_answer_basic.html', {'dbtest_data': data})

from django.http import HttpResponse
from .models import Regime, Schedule, Section, User, Permission

def load_dummy_data_1(request):
    # --- Regimes ---
    regimes = [
        Regime(regime_id="HMRC_IHT", regime_name="HMRC – Inheritance Tax"),
        Regime(regime_id="DWP_UC", regime_name="DWP – Universal Credit"),
    ]
    Regime.objects.bulk_create(regimes, ignore_conflicts=True)

    # --- Schedules ---
    schedules = [
        Schedule(schedule_id="IHT_bank", schedule_name="Bank Accounts", regime_id="HMRC_IHT"),
        Schedule(schedule_id="IHT_property", schedule_name="Property & Assets", regime_id="HMRC_IHT"),
        Schedule(schedule_id="UC_family", schedule_name="Household & Family", regime_id="DWP_UC"),
        Schedule(schedule_id="UC_housing", schedule_name="Housing Costs", regime_id="DWP_UC"),
    ]
    Schedule.objects.bulk_create(schedules, ignore_conflicts=True)

    # --- Sections ---
    sections = [
        Section(section_id="IHT_bank_UKbank", section_name="UK Bank Accounts", schedule_id="IHT_bank"),
        Section(section_id="IHT_bank_NS", section_name="National Savings & Investments", schedule_id="IHT_bank"),
        Section(section_id="IHT_property_home", section_name="Main Residence", schedule_id="IHT_property"),
        Section(section_id="IHT_property_other", section_name="Other Properties", schedule_id="IHT_property"),
        Section(section_id="UC_family_children", section_name="Children and Dependents", schedule_id="UC_family"),
        Section(section_id="UC_family_income", section_name="Partner Income", schedule_id="UC_family"),
        Section(section_id="UC_housing_rent", section_name="Rent and Tenancy", schedule_id="UC_housing"),
        Section(section_id="UC_housing_bills", section_name="Utility Bills", schedule_id="UC_housing"),
    ]
    Section.objects.bulk_create(sections, ignore_conflicts=True)

    # --- Users ---
    users = [
        User(user_id="user_alice", user_name="Alice Johnson"),        # Partial IHT
        User(user_id="user_bob", user_name="Bob Smith"),              # Partial UC
        User(user_id="user_carla", user_name="Carla Hughes"),        # Full IHT
        User(user_id="user_dan", user_name="Dan Patel"),             # Full UC
        User(user_id="user_eve", user_name="Eve Miller"),            # Full ALL
    ]
    User.objects.bulk_create(users, ignore_conflicts=True)

    # --- Permissions ---
    permissions = [
        # Partial access
        Permission(user_id="user_alice", section_id="IHT_bank_UKbank"),
        Permission(user_id="user_alice", section_id="IHT_bank_NS"),
        Permission(user_id="user_bob", section_id="UC_family_income"),
        Permission(user_id="user_bob", section_id="UC_housing_rent"),
    ]

    # Full access for Carla (HMRC_IHT)
    iht_sections = Section.objects.filter(schedule__regime_id="HMRC_IHT")
    permissions += [
        Permission(user_id="user_carla", section=section) for section in iht_sections
    ]

    # Full access for Dan (DWP_UC)
    uc_sections = Section.objects.filter(schedule__regime_id="DWP_UC")
    permissions += [
        Permission(user_id="user_dan", section=section) for section in uc_sections
    ]

    # Full access for Eve (all sections)
    all_sections = Section.objects.all()
    permissions += [
        Permission(user_id="user_eve", section=section) for section in all_sections
    ]

    Permission.objects.bulk_create(permissions, ignore_conflicts=True)

    return HttpResponse("Dummy data loaded successfully.")

def load_dummy_data_2(request):
    # --- Add Simple Regime ---
    simple_regime = Regime(regime_id="DWP_FG", regime_name="DWP – Funeral Grant")
    Regime.objects.get_or_create(regime_id="DWP_FG", defaults={"regime_name": "DWP – Funeral Grant"})

    # --- Add Section for Simple Regime (no schedule) ---
    Section.objects.get_or_create(
        section_id="FG_details",
        defaults={
            "section_name": "Funeral grant form",
            "regime_id": "DWP_FG"  # direct link to regime
        }
    )

    # --- Give Eve permission for simple regime too
    Permission.objects.get_or_create(user_id="user_eve", section_id="FG_details")

def load_dummy_data(request):
    questions = [
        Question(
            question_id="FG_Q1",
            question_type="text",
            question_text="What is your full name?",
            hint="As shown on official documents.",
            answer_type="text",
        ),
        Question(
            question_id="FG_Q2",
            question_type="text",
            question_text="Please briefly describe your relationship to the deceased.",
            guidance="Include any relevant details like family or friend.",
            answer_type="text",
        ),
        Question(
            question_id="FG_Q3",
            question_type="radio",
            question_text="Are you currently receiving any benefits?",
            options="Yes;No",
            answer_type="text",
        ),
        Question(
            question_id="FG_Q4",
            question_type="checkbox",
            question_text="Which of the following costs are you applying for?",
            guidance="Tick all that apply.",
            options="Funeral Director fees; Cremation or burial; Travel expenses; Medical certificates",
            answer_type="text",
        )
    ]

    Question.objects.bulk_create(questions, ignore_conflicts=True)

    routings = [
        Routing(
            section_id="FG_onepage",
            current_question="FG_Q1",
            next_question="FG_Q2"
        ),
        Routing(
            section_id="FG_onepage",
            current_question="FG_Q2",
            next_question="FG_Q3"
        ),
        Routing(
            section_id="FG_onepage",
            current_question="FG_Q3",
            next_question="FG_Q4"
        ),
        Routing(
            section_id="FG_onepage",
            current_question="FG_Q4",
            next_question="END"
        )
    ]

    Routing.objects.bulk_create(routings, ignore_conflicts=True)

    return HttpResponse("Dummy data loaded successfully.")