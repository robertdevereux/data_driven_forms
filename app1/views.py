import csv, json, bleach
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.contrib import messages
from urllib.parse import urlencode
from .models import Permission, Regime, Schedule, Section, Routing, Question

ALLOWED_TAGS = ["b", "i", "u", "strong", "em", "h1", "h2", "h3", "p", "ul", "ol", "li", "br"]

def consistency_check(request):

    # ✅ Step 1: Retrieve all questions and routing data
    question_ids = set(Question.objects.values_list("question_id", flat=True))
    routing_data = list(Routing.objects.values("section_id", "current_question", "next_question", "answer_value"))

    errors = []

    # ✅ Step 2: Check (a) - Ensure all `current_question` and `next_question` exist in `Question`
    for route in routing_data:
        section_id = route["section_id"]
        current_q = route["current_question"]
        next_q = route["next_question"]

        if current_q not in question_ids:
            errors.append(
                f"Section '{section_id}': Routing error - current_question '{current_q}' does not exist in Question table.")

        if next_q and next_q != "END" and next_q not in question_ids:
            errors.append(
                f"Section '{section_id}': Routing error - next_question '{next_q}' does not exist in Question table.")

    # ✅ Step 3: Check (b) - Ensure every `answer_value` in Routing exists in `Question.options`
    question_options = {
        q.question_id: set(q.options.split("; ")) if q.options else set()  # Convert options to set for easy checking
        for q in Question.objects.all()
    }

    for route in routing_data:
        section_id = route["section_id"]
        current_q = route["current_question"]
        answer_value = route["answer_value"]

        if answer_value and current_q in question_options:
            valid_options = question_options[current_q]  # Get allowed options for this question
            provided_answers = set(answer_value.split("; "))  # Split Routing's answer_value into a set

            if not provided_answers.issubset(valid_options):  # Check if all answers are valid
                errors.append(
                    f"Section '{section_id}': Routing error - current_question '{current_q}' has invalid answer_value '{answer_value}'. "
                    f"Valid options: {valid_options}"
                )

    # ✅ Step 4: If errors exist, exit and show them
    print("Errors",errors)
    if errors:

        return HttpResponse(
            "<h3>Database Consistency Check Failed</h3>"
            "<p>The question set and routing set are inconsistent. Fix the following issues:</p>"
            "<ul>" + "".join([f"<li>{error}</li>" for error in errors]) + "</ul>"
        )

    return redirect('user_login')

def user_login(request):

    message = None  # Default message

    # on user completion of login.html
    if request.method == "POST":
        user_id = request.POST.get("user_id", "").strip() # capture form data
        permissions = Permission.objects.filter(user_id=user_id)
        if permissions.exists(): # Store all permission records in session
            request.session["permissions"] = list(permissions.values())  # Convert QuerySet to list of dicts
            request.session["user_id"] = user_id  # Store user_id for reference
            request.session.modified = True
            print("******************** user_id was: ", user_id)
            print("******************** this user has this many permissions: ", len(permissions))
            return redirect("select_regime")  # Redirect to next step
        else:
            message = "No such User_ID" # view carries on to refresh login.html with this error message

    # preparation of login.html: first time with default message at top, else with error message above
    return render(request, "app1/login.html", {"message": message})

def select_regime(request):
    # on user completion of select_regime.html
    if request.method == "POST":
        selected_regime_id = request.POST.get("selected_regime", "").strip() # capture form data
        regimes = request.session.get("regimes", {}) # Retrieve stored regimes from session (populated in GET request below)
        if not selected_regime_id or selected_regime_id not in regimes:
            print("Invalid regime selected!")  # Debugging step
            return render(request, "app1/select_regime.html", {"regimes": regimes, "error": "Please select a valid regime."})
        request.session["selected_regime_id"] = selected_regime_id # Store the selected regime in session
        request.session.modified = True
        print("****************** Selected regime was", selected_regime_id, " ", regimes[selected_regime_id])
        print("DEBUG: Current session data:", request.session.items())  # ✅ Print full session contents
        print("DEBUG: Selected regime:", request.session.get("selected_regime_id"))  # ✅ Confirm regime selection is stored

        return redirect("select_schedule") # Redirect to select_schedule

    # Preparation of select_regime.html
    permissions = request.session.get("permissions", []) # collect previously stored permissions for this user
    if not permissions:
        return HttpResponse("request.session.get['permissions'] is empty")
    regime_ids = {perm["regime_id"] for perm in permissions} # Extract unique permitted regime_ids
    regimes = { # Fetch regime names from Regime model
        str(regime.regime_id): regime.regime_name
        for regime in Regime.objects.filter(regime_id__in=regime_ids)
    }
    print("***************** Regimes available:", regimes)  # Debugging step
    request.session["regimes"] = regimes # Store regimes in session for later use
    request.session.modified = True
    return render(request, "app1/select_regime.html", {"regimes": regimes})

def select_schedule(request):
    # on user completion of select_schedule.html
    if request.method == "POST":
        selected_schedule_id = request.POST.get("selected_schedule", "").strip() # capture form data
        schedules = request.session.get("schedules", {}) # Retrieve stored schedules from session
        if not selected_schedule_id or selected_schedule_id not in schedules:
            print("Invalid schedule selected!")  # Debugging step
            return render(request, "app1/select_schedule.html", {"schedules": schedules, "error": "Please select a valid schedule."})
        request.session["selected_schedule_id"] = selected_schedule_id # Store selected schedule in session
        request.session.modified = True
        print("****************** Selected schedule was", selected_schedule_id, " ", schedules[selected_schedule_id])
        print("DEBUG: Selected schedule:", request.session.get("selected_schedule_id"))
        return redirect("select_section") # Redirect to the section selection step

    # Preparation of select_schedule.html
    permissions = request.session.get("permissions", []) # Retrieve stored permissions for current user
    selected_regime_id = request.session.get("selected_regime_id", "") # Retrieve selected_regime
    print("Selected regime id:", selected_regime_id)  # Debugging step
    if not selected_regime_id:
        print("Error: selected_regime is missing from session!")
        return redirect("select_regime")
    schedule_ids = { # Extract unique permitted schedules for the selected regime
        perm["schedule_id"]
        for perm in permissions
        if perm["regime_id"] == selected_regime_id
    }
    schedules = { # Fetch schedule details from Schedule model
        str(schedule.schedule_id): schedule.schedule_name
        for schedule in Schedule.objects.filter(schedule_id__in=schedule_ids)
    }
    print("************** Schedules available:", schedules)  # Debugging step
    request.session["schedules"] = schedules # Store schedules in session
    request.session.modified = True
    return render(request, "app1/select_schedule.html", {"schedules": schedules})


def select_section(request):
    # On user completion of select_section.html
    if request.method == "POST":
        selected_section_id = request.POST.get("selected_section", "").strip()  # Capture form data
        print("Selected section from html:" , selected_section_id)
        sections = request.session.get("sections", {})  # Retrieve stored sections from session

        if not selected_section_id or selected_section_id not in sections:
            return render(request, "app1/select_section.html",
                          {"sections": sections, "error": "Please select a valid section."})

        request.session["selected_section_id"] = selected_section_id  # Store selected section in session

        # Fetch routing data for selected section
        routing_data = list(Routing.objects.filter(section_id=selected_section_id).values())
        request.session["routing_table"] = routing_data

        # Extract all relevant question IDs from routing (avoiding duplicates)
        question_ids = {route["current_question"] for route in routing_data}
        print("Questions needed for this section:", question_ids)  # Debugging step

        # ✅ FIX: Change `id` to `question_id`
        questions = Question.objects.filter(question_id__in=question_ids)

        # Store questions in session as a dictionary {question_id: question_data}
        request.session["question_table"] = {
            str(question.question_id): {
                "text": question.question_text,
                "guidance": question.guidance,
                "hint": question.hint,
                "question_type": question.question_type,
                "options": question.options if question.options else "",  # ✅ Ensure options is stored properly
            }
            for question in questions
        }

        request.session.modified = True  # Ensure session updates
        print("*********************", selected_section_id, " chosen, and ", str(len(routing_data)),
              " routing rules loaded.")

        first_current_question = routing_data[0]["current_question"]
        return redirect("question_router", question_id=first_current_question)

    # Preparation of select_section.html
    permissions = request.session.get("permissions", [])
    selected_regime_id = request.session.get("selected_regime_id", "")
    selected_schedule_id = request.session.get("selected_schedule_id", "")
    print("******* PREPARING FOR SECTION HTML: ", permissions, selected_regime_id, selected_schedule_id)

    if not permissions or not selected_regime_id or not selected_schedule_id:
        return HttpResponse("Problem in select_section")  # Redirect if data is missing

    section_ids = {  # Extract unique permitted sections for the selected regime and schedule
        perm["section_id"]
        for perm in permissions
        if perm["regime_id"] == selected_regime_id and perm["schedule_id"] == selected_schedule_id
    }
    print("Section_ids: ", section_ids)
    sections = {  # Fetch relevant sections from Section model
        str(section.section_id): section.section_name
        for section in Section.objects.filter(section_id__in=section_ids)
    }

    print("******************** Sections available:", sections)  # Debugging step
    request.session["sections"] = sections  # Store sections in session
    request.session.modified = True

    return render(request, "app1/select_section.html", {"sections": sections})

def question_router(request, question_id):
    question = request.session["question_table"].get(str(question_id))

    if not question:
        return HttpResponseNotFound(f"Question data for question id {question_id} not found in session.")  # ✅ Fixed error

    # ✅ Use `question_type` to determine the correct screen type
    if question["question_type"].lower() == "radio":
        return redirect("radio_view", question_id=question_id)
    elif question["question_type"].lower() == "text":
        return redirect("text_view", question_id=question_id)
    elif question["question_type"].lower() == "textarea":
        return redirect("textarea_view", question_id=question_id)
    elif question["question_type"].lower() == "checkbox":
        return redirect("checkbox_view", question_id=question_id)
    else:
        print(f"Unknown question type for {question_id}: {question['question_type']}")
        return redirect("completion_page")  # ✅ Default fallback

def radio_view(request, question_id):
    question = request.session["question_table"].get(str(question_id))

    if not question:
        return HttpResponseNotFound(f"Question data for question id {question_id} not found in session.")

    print(f"Question ID: {question_id}")
    print(f"Stored question data: {question}")

    return render(request, "app1/radio_template.html", {
        "question_id": question_id,
        "question_text": question["text"],
        "guidance": bleach.clean(question["guidance"], tags=ALLOWED_TAGS) if question["guidance"] else "",
        "hint": bleach.clean(question["hint"], tags=ALLOWED_TAGS) if question["hint"] else "",
        "options": question["options"].split(";") if question.get("options") else [],
    })

def text_view(request, question_id):
    question = request.session["question_table"].get(str(question_id))

    if not question:
        return HttpResponseNotFound(f"Question data for question id {question_id} not found in session.")

    print(f"Question ID: {question_id}")
    print(f"Stored question data: {question}")

    return render(request, "app1/text_template.html", {
        "question_id": question_id,
        "question_text": question["text"],
        "guidance": bleach.clean(question["guidance"], tags=ALLOWED_TAGS) if question["guidance"] else "",
        "hint": bleach.clean(question["hint"], tags=ALLOWED_TAGS) if question["hint"] else "",
    })

def textarea_view(request, question_id):
    question = request.session["question_table"].get(str(question_id))

    if not question:
        return HttpResponseNotFound(f"Question data for question id {question_id} not found in session.")

    print(f"Question ID: {question_id}")
    print(f"Stored question data: {question}")

    return render(request, "app1/textarea_template.html", {
        "question_id": question_id,
        "question_text": question["text"],
        "guidance": bleach.clean(question["guidance"], tags=ALLOWED_TAGS) if question["guidance"] else "",
        "hint": bleach.clean(question["hint"], tags=ALLOWED_TAGS) if question["hint"] else "",
    })

def checkbox_view(request, question_id):
    question = request.session["question_table"].get(str(question_id))

    if not question:
        return HttpResponseNotFound(f"Question data for question id {question_id} not found in session.")

    print(f"Question ID: {question_id}")
    print(f"Stored question data: {question}")

    return render(request, "app1/checkbox_template.html", {
        "question_id": question_id,
        "question_text": question["text"],
        "guidance": bleach.clean(question["guidance"], tags=ALLOWED_TAGS) if question["guidance"] else "",
        "hint": bleach.clean(question["hint"], tags=ALLOWED_TAGS) if question["hint"] else "",
        "options": question["options"].split(";") if question.get("options") else [],
    })

def process_answer(request, question_id):
    if request.method == "POST":
        # Retrieve the question from session storage instead of querying the database
        question = request.session["question_table"].get(str(question_id))

        if not question:
            return HttpResponseNotFound(f"Question data for question id {question_id} not found in session.")

        # ✅ Use `question_type` to handle response correctly
        if question["question_type"] == "checkbox":
            user_response = request.POST.getlist("question")  # List of selections
            user_response_str = "; ".join(user_response)  # Store as semicolon-separated string
        else:
            user_response = request.POST.get("question", "").strip()

        print(f"User's answer for {question_id}: {user_response}")

        # Store user response in session
        if "user_answers" not in request.session:
            request.session["user_answers"] = {}
        request.session["user_answers"][str(question_id)] = user_response
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
            if route["current_question"] == str(question_id):  # ✅ Fix field name to match session data
                if route["answer_value"]:  # Conditional routing
                    allowed_answers = [ans.strip().lower() for ans in route["answer_value"].split(";")]
                    if user_response.lower() in allowed_answers:
                        next_question_id = route["next_question"]
                        break
                else:  # Default routing
                    next_question_id = route["next_question"]

        # ✅ If next_question_id is "END", redirect to the completion page
        if next_question_id == "END":
            return redirect("completion_page")

        # ✅ Handle missing next question
        if not next_question_id:
            error_message = f"No valid next question found for '{question_id}' with answer '{user_response}'."
            print(error_message)
            return redirect(f"/app1/completion/?{urlencode({'error_message': error_message})}")

        return redirect("question_router", question_id=next_question_id)

    return redirect("question_router", question_id=question_id)

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


