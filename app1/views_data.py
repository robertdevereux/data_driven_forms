import csv, re

from django.http import HttpResponse
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

from django.shortcuts import render, redirect
from django.contrib import messages
import csv
from .models import Question

import csv
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Question


def upload_questions(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']

        # Decode file and ensure correct parsing with quoted fields
        reader = csv.reader(file.read().decode('utf-8', errors='ignore').splitlines(), quotechar='"')

        next(reader)  # Skip header row

        for row in reader:
            row = (row + [None] * 8)[:8]  # Ensure row has at least 8 columns

            # Inline cleaning: Remove control characters & trim whitespace
            row = [re.sub(r'[\x00-\x1F\x7F-\x9F]', '', value).strip() if value else None for value in row]
            '''
            if len(row) != 8:
                print(f"❌ Invalid row length ({len(row)} columns instead of 8): {row}")
                return HttpResponse("Invalid row format - Incorrect column count")

            if (
                    (row[0] and len(row[0].strip()) > 50) or
                    (row[3] and len(row[3].strip()) > 255) or
                    (row[4] and len(row[4].strip()) > 20) or
                    (row[6] and len(row[6].strip()) > 20)
            ):
                print("❌ FIELD LENGTH ERROR ❌")
                print(f"Raw row: {row}")
                print(f"QID: {row[0]} ({len(row[0].strip()) if row[0] else 0})")
                print(f"Hint: {row[3]} ({len(row[3].strip()) if row[3] else 0})")
                print(f"Question Type: {row[4]} ({len(row[4].strip()) if row[4] else 0})")
                print(f"Answer Type: {row[6]} ({len(row[6].strip()) if row[6] else 0})")
                return HttpResponse("Field lengths out of range")

            # Skip rows with missing required fields
            if not row[0] or not row[2] or not row[4] or not row[6]:  # Ensure `question_type` is not null
                print("Critical fields missing: ", row)
                return HttpResponse("Critical fields missing")

            if row[4] and row[4].strip().lower() in ["radio", "checkbox"]:
                if not row[5] or len(row[5].strip()) == 0:
                    print("❌ ERROR: Radio or checkbox question missing options.")
                    print(f"Debug Options: '{row[5]}' (Length: {len(row[5])})")
                    return HttpResponse("Radio or checkbox question without answer options")

            print("************* INSERTING INTO DATABASE *************")
            print(f"Row Length: {len(row)}, Expected: 8")
            print(f"Row Data: {row}")
            print(f"QID: '{row[0]}'")
            print(f"Guidance: '{row[1]}'")
            print(f"Question Text: '{row[2]}'")
            print(f"Hint: '{row[3]}'")
            print(f"Question Type: '{row[4]}' (Length: {len(row[4]) if row[4] else 0})")
            print(f"Options: '{row[5]}'")
            print(f"Answer Type: '{row[6]}' (Length: {len(row[6]) if row[6] else 0})")
            print(f"Parent Question ID: '{row[7]}'")
            print(f"Options (ASCII): {[ord(c) for c in row[5]]}" if row[5] else "Options is empty!")

            # Verify field mapping before saving
            if len(row[4]) > 20 or len(row[6]) > 20:
                print("❌ Field length too long before saving. Investigate CSV column mapping.")
                return HttpResponse("Field length validation failed!")

            
            Question.objects.update_or_create(
                question_id=row[0],
                defaults={
                    'guidance': row[1],
                    'question_text': row[2],
                    'hint': row[3],
                    'question_type': row[4],
                    'answer_type': row[5],
                    'options': row[6] if row[6] else None,
                    'parent_question_id': row[7] if row[7] else None
                }
            )
            '''

            mapped_data = {
                'guidance': row[1] if row[1] else None,
                'question_text': row[2],
                'hint': row[3] if row[3] else None,
                'question_type': row[4],
                'options': row[5] if row[5] else None,
                'answer_type': row[6],  # Double-checking if row[6] is correct
                'parent_question_id': row[7] if row[7] else None
            }
            '''
            print("************* FINAL MAPPED DATA BEFORE SAVE *************")
            for key, value in mapped_data.items():
                print(f"{key}: {value} (Length: {len(value) if value else 0})")

            # 🚨 Block insertion if any value is too long
            if len(row[4]) > 20 or len(row[6]) > 20:
                print(
                    f"❌ ERROR: Field too long: QT='{row[4]}' (Length {len(row[4])}), AT='{row[6]}' (Length {len(row[6])})")
                return HttpResponse("Field length validation failed!")
            '''
            # Perform the database insertion
            try:
                Question.objects.update_or_create(question_id=row[0], defaults=mapped_data)
            except:
                print(mapped_data)

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



