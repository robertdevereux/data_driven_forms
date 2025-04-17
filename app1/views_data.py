import csv, re, io

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Regime, Schedule, Section, Routing, Question, Question2, Permission, AnswerBasic, AnswerTable
from .forms import RegimeForm, ScheduleForm, SectionForm  # We'll create these forms

def clean_uploaded_csv(file, expected_field_count=None, strict_column_check=True):
    """
    Cleans and returns rows from a CSV file-like object.

    Args:
        file: Django UploadedFile (request.FILES['file'])
        expected_field_count: int, optional
        strict_column_check: bool, if True, raises on non-empty extra columns

    Returns:
        (header, rows): list of header columns, list of cleaned row lists

    Raises:
        ValueError if header is missing or if rows are malformed
    """
    content = file.read().decode('utf-8', errors='ignore')
    print(f"📏 Raw content length: {len(content)}")

    # Normalize line endings
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    raw_lines = content.split('\n')

    # Remove fully empty lines (just whitespace or commas)
    meaningful_lines = []
    for line in raw_lines:
        fields = [f.strip() for f in line.split(',')]
        if any(field for field in fields):
            meaningful_lines.append(','.join(fields))

    print(f"🧹 Non-empty lines: {len(meaningful_lines)}")

    # Strip control characters
    cleaned_lines = [re.sub(r'[\x00-\x1F\x7F-\x9F]', '', line) for line in meaningful_lines]

    print("🧪 Sample cleaned lines:")
    for i, line in enumerate(cleaned_lines[:5]):
        print(f"  {i+1}: {repr(line)} — {line.count(',')} commas")

    # Parse with CSV reader
    csvfile = io.StringIO('\n'.join(cleaned_lines))
    reader = csv.reader(csvfile)

    try:
        header = next(reader)
        print(f"🧠 Header: {header}")
    except StopIteration:
        raise ValueError("Empty or invalid CSV file — no header row found.")

    rows = []
    for i, row in enumerate(reader, start=2):
        base_fields = row[:len(header)]
        extra_fields = row[len(header):]

        # Check for unexpected data in extra fields
        if strict_column_check and extra_fields and any(f.strip() for f in extra_fields):
            raise ValueError(f"❌ Row {i} has unexpected extra data columns: {extra_fields}")

        rows.append(base_fields)

    if expected_field_count and len(header) != expected_field_count:
        raise ValueError(
            f"❌ Expected {expected_field_count} columns, but header has {len(header)}."
        )

    return header, rows

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

def upload_routing2(request):
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

def upload_routing(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            header, rows = clean_uploaded_csv(
                request.FILES['file'],
                expected_field_count=4,
                strict_column_check=True
            )
        except ValueError as e:
            messages.error(request, f"❌ Error: {str(e)}")
            return redirect('upload_routing')

        success_count = 0
        error_count = 0

        for i, row in enumerate(rows, start=2):
            row = [cell.strip() if cell else None for cell in row]

            try:
                Routing.objects.update_or_create(
                    section_id=row[0],
                    current_question=row[1],
                    answer_value=row[2],  # Can be blank/None
                    defaults={'next_question': row[3]}
                )
                print(f"✅ Row {i}: Routing loaded for {row[0]} → {row[3]}")
                success_count += 1
            except Exception as e:
                print(f"❌ Row {i} error: {e}")
                error_count += 1

        messages.success(
            request,
            f"✅ Routing upload complete: {success_count} loaded, {error_count} errors."
        )
        return redirect('upload_routing')

    return render(request, 'app1/upload_csv.html', {'data_name': 'Routing'})

def upload_questions(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            header, rows = clean_uploaded_csv(
                request.FILES['file'],
                expected_field_count=8, # matching the number of fields in mapped_data below, plus question_id
                strict_column_check=True # throws an error if file has data beyond first 8 cols
            )
        except ValueError as e:
            messages.error(request, f"❌ Error: {str(e)}")
            return redirect('upload_questions')

        error_count=0
        success_count=0

        for i, row in enumerate(rows, start=2):
            # Ensure row has exactly 8 fields
            row = (row + [None] * 8)[:8]
            row = [cell.strip() if cell else None for cell in row]

            mapped_data = {
                'guidance': row[1],
                'question_text': row[2],
                'hint': row[3],
                'question_type': row[4],
                'options': row[5],
                'answer_type': row[6],
                'parent_question_id': row[7],
            }

            question_id = row[0]
            if not question_id:
                print(f"⚠️ Skipping row {i}: missing question ID")
                error_count += 1
                continue

            try:
                Question.objects.update_or_create(
                    question_id=question_id,
                    defaults=mapped_data
                )
                #print(f"✅ Row {i}: Loaded question {question_id}")
                success_count += 1
            except Exception as e:
                print(f"❌ Row {i} error: {e}")
                error_count += 1

        messages.success(
            request,
            f"✅ Upload complete: {success_count} questions loaded, {error_count} errors. See console for details."
        )
        return redirect('upload_questions')

    else:
        messages.error(request, "No file uploaded.")
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
    data = Routing.objects.order_by('section_id', 'order_in_section').all()
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

def load_dummy_data(request):
    # --- Regimes ---
    regimes = [
        Regime(regime_id="HMRC_IHT", regime_name="HMRC – Inheritance Tax"),
        Regime(regime_id="DWP_UC",   regime_name="DWP – Universal Credit"),
        Regime(regime_id="DWP_FG",   regime_name="DWP – Funeral Grant")
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
        Section(section_id="FG_details",section_name="Funeral grant form", regime_id="DWP_FG")
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
            section_id="FG_details",
            current_question="FG_Q1",
            next_question="FG_Q2"
        ),
        Routing(
            section_id="FG_details",
            current_question="FG_Q2",
            next_question="FG_Q3"
        ),
        Routing(
            section_id="FG_details",
            current_question="FG_Q3",
            next_question="FG_Q4"
        ),
        Routing(
            section_id="FG_details",
            current_question="FG_Q4",
            next_question="END"
        )
    ]

    Routing.objects.bulk_create(routings, ignore_conflicts=True)

    return HttpResponse("Dummy data loaded successfully.")