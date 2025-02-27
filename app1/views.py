import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from urllib.parse import urlencode
from .models import ScreenQuestion, ScreenRouting, Service

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

def select_service(request):
    if request.method == "POST":
        service_id = request.POST.get("service_id")  # Get selected service
        print(f"DEBUG: Received service_id = {service_id}")  # Debugging

        if not service_id:
            return HttpResponse("No service selected", status=400)

        request.session["service_id"] = service_id
        routing_data = list(ScreenRouting.objects.filter(service_id=service_id).values())
        request.session["routing_table"] = routing_data
        request.session.modified = True

        print(f"Service {service_id} selected, loaded {len(routing_data)} routing rules.")
        return redirect("question_router", question_id="Q1")

    services = Service.objects.all()
    return render(request, "app1/select_service.html", {"services": services})

def question_router(request, question_id):
    question = get_object_or_404(ScreenQuestion, id=question_id)

    # ✅ Use `question_type` to determine the correct screen type
    if question.question_type == "radio":
        return redirect("radio_view", question_id=question_id)
    elif question.question_type == "text":
        return redirect("text_view", question_id=question_id)
    elif question.question_type == "checkbox":  # ✅ Correctly route to checkbox view
        return redirect("checkbox_view", question_id=question_id)
    else:
        print(f"Unknown question type for {question_id}: {question.question_type}")
        return redirect("completion_page")  # If `question_type` is unrecognized


def radio_view(request, question_id):
    question = get_object_or_404(ScreenQuestion, id=question_id)

    # Ensure options are correctly split into a list
    options = question.options.split(";") if question.options else []

    return render(request, "app1/radio_template.html", {
        "question_id": question_id,  # Ensure question_id is passed
        "question_text": question.question_text,
        "options": options,
        "question_guidance" : '<script>alert("XSS Attack!");</script>'
 #"<h1 class='govuk-heading-1'>Freeports</h1>"
    })

def text_view(request, question_id):
    question = get_object_or_404(ScreenQuestion, id=question_id)

    return render(request, "app1/text_template.html", {
        "question_id": question_id,  # Ensure question_id is passed
        "question_text": question.question_text
    })

def checkbox_view(request, question_id):
    question = get_object_or_404(ScreenQuestion, id=question_id)
    options = question.options.split(";") if question.options else []

    return render(request, "app1/checkbox_template.html", {
        "question_id": question_id,
        "question_text": question.question_text,
        "options": options
    })

import json
from django.shortcuts import render, redirect, get_object_or_404

def process_answer(request, question_id):
    if request.method == "POST":
        question = get_object_or_404(ScreenQuestion, id=question_id)

        # ✅ Use `question_type` to handle response correctly
        if question.question_type == "checkbox":
            user_response = request.POST.getlist("question")  # List of selections
            user_response_str = "; ".join(user_response)  # Store as semicolon-separated string
        else:
            user_response = request.POST.get("question", "").strip()

        print(f"User's answer for {question_id}: {user_response}")

        # Store user response in session
        if "user_answers" not in request.session:
            request.session["user_answers"] = {}
        request.session["user_answers"][question_id] = user_response
        request.session.modified = True  # Save session updates

        # ✅ Generate JSON string for all collected answers
        json_data = json.dumps({
            "service_id": request.session.get("service_id", "unknown_service"),
            "responses": request.session["user_answers"]
        }, indent=4)  # Pretty-print JSON for readability

        # ✅ Store JSON in session for display on completion page
        request.session["final_json"] = json_data

        # Retrieve routing table
        routing_table = request.session.get("routing_table", [])

        # Determine next question
        next_question_id = None
        for route in routing_table:
            if route["current_id"] == question_id:
                if route["answer_value"]:  # Conditional routing
                    allowed_answers = [ans.strip().lower() for ans in route["answer_value"].split(";")]
                    if user_response.lower() in allowed_answers:
                        next_question_id = route["next_id"]
                        break
                else:  # Default routing
                    next_question_id = route["next_id"]

        # ✅ If next_question_id is "END", redirect to the completion page
        if next_question_id == "END":
            return redirect("completion_page")

        # ✅ Handle missing next question
        if not next_question_id:
            error_message = f"No valid next question found for '{question_id}' with answer '{user_response}'."
            print(error_message)
            from urllib.parse import urlencode
            return redirect(f"/app1/completion/?{urlencode({'error_message': error_message})}")

        return redirect("question_router", question_id=next_question_id)

    return redirect("question_router", question_id=question_id)

def completion_page(request):
    error_message = request.GET.get("error_message", "")  # Extract error message if any
    final_json = request.session.get("final_json", "{}")  # Retrieve stored JSON

    return render(request, "app1/completion.html", {
        "error_message": error_message,
        "final_json": final_json
    })

def restart_process(request):
    # ✅ Remove stored user answers & JSON data
    request.session.pop("user_answers", None)
    request.session.pop("final_json", None)
    request.session.pop("service_id", None)
    request.session.pop("routing_table", None)

    request.session.modified = True  # Ensure session is updated

    print("Session cleared. Restarting process.")  # Debugging

    return redirect("select_service")  # Redirect back to service selection

def screen1(request):
    return render(request, 'app1/screen1.html')

def app1_home(request):
    return HttpResponse("This is the home page of the app app1")

def p2(request):
    return HttpResponse("This is the 2nd page of the app app1")



