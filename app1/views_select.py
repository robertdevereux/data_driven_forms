from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Permission, Regime, Schedule, Section, Routing, Question, ScheduleStatus, SectionStatus

def model_to_dict(model, unique_field):
    # unique field is a string; model is just the model name (not a string)
    return {
        obj[unique_field]: {k: v for k, v in obj.items() if k != unique_field}
        for obj in model.objects.values()
    }

def consistency_check(request):

    # Retrieve all questions and routing data; create errors variable
    question_ids = set(Question.objects.values_list("question_id", flat=True)) # set gives faster lookup using 'in'
    routing_data = list(Routing.objects.values("section_id", "current_question", "next_question", "answer_value"))
    errors = []

    # Check 1 - Ensure all `current_question` and `next_question` exist in `Question`
    for route in routing_data:
        section_id = route["section_id"]
        current_q = route["current_question"]
        next_q = route["next_question"]

        if current_q not in question_ids:
            errors.append(
                f"Routing error in Section '{section_id}': current_question '{current_q}' does not exist in Question table.")

        if next_q and next_q != "END" and next_q not in question_ids:
            errors.append(
                f"Routing error in Section '{section_id}': next_question '{next_q}' does not exist in Question table.")

    # Check 2 - Ensure every `answer_value` in Routing exists in `Question.options`
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
                    f"Routing error in Section '{section_id}':  current_question {current_q}' has invalid answer_value '{answer_value}'. "
                    f"Valid options: {valid_options}"
                )

    # If errors exist, show them then exit via HttpResponse
    print("Errors",errors)
    if errors:
        return HttpResponse(
            "<h3>The data on questions and routing has failed the consistency checks</h3>"
            "<p>Fix the following issues:</p>"
            "<ul>" + "".join([f"<li>{error}</li>" for error in errors]) + "</ul>"
        )

    # if no errors, continue to user login
    return redirect('user_login')

def user_login(request):
    message = None  # Default message

    if request.method == "POST":
        user_id = request.POST.get("user_id", "").strip()

        # Pull all permitted section_ids for the user
        section_ids = (
            Permission.objects
            .filter(user_id=user_id)
            .values_list("section_id", flat=True)
            .distinct()
        )

        if section_ids:  # If user exists and has permissions
            request.session["user_id"] = user_id
            request.session["select_dict"] = {"user_id": user_id} # initalise new select_dict
            request.session["section_ids"] = list(section_ids)
            request.session.modified = True
            return redirect("select_regime")
        else:
            message = "No such user_id with valid permissions"

    return render(request, "app1/login.html", {"message": message})

def select_regime(request):
    if request.method == "POST":
        selected_regime_id = request.POST.get("selected_regime")
        regimes = request.session.get("regimes", {})

        if not selected_regime_id or selected_regime_id not in regimes:
            return HttpResponse("Something that should be impossible has occurred in select_regime")

        # Update session context
        select_dict = request.session.get("select_dict", {})
        select_dict["regime_id"] = selected_regime_id
        select_dict["regime_name"] = regimes[selected_regime_id]

        request.session["selected_regime_id"] = selected_regime_id
        request.session["select_dict"] = select_dict
        request.session.modified = True

        return redirect("select_schedule")

    # On GET: derive regimes from permitted sections
    section_ids = request.session.get("section_ids", [])

    regime_ids = (
        Section.objects.filter(section_id__in=section_ids)
        .values_list("schedule__regime_id", flat=True)
        .distinct()
    )

    regimes = {
        str(regime.regime_id): regime.regime_name
        for regime in Regime.objects.filter(regime_id__in=regime_ids)
    }

    request.session["regimes"] = regimes
    request.session.modified = True

    return render(request, "app1/select_regime.html", {"regimes": regimes})

def select_schedule(request):
    user_id = request.session.get("user_id")
    regime_id = request.session.get("selected_regime_id")
    section_ids = request.session.get("section_ids", [])

    # Get schedules the user can access under this regime
    schedule_ids = (
        Section.objects.filter(section_id__in=section_ids, schedule__regime_id=regime_id)
        .values_list("schedule_id", flat=True)
        .distinct()
    )

    schedules = Schedule.objects.filter(schedule_id__in=schedule_ids).values("schedule_id", "schedule_name")

    # Get schedule completion statuses
    schedule_statuses = {
        status["schedule_id"]: status["status"]
        for status in ScheduleStatus.objects.filter(user_id=user_id, regime_id=regime_id).values("schedule_id", "status")
    }

    progress = [
        {
            "schedule_id": schedule["schedule_id"],
            "name": schedule["schedule_name"],
            "href": f"/select_section/{schedule['schedule_id']}/",
            "status": schedule_statuses.get(schedule["schedule_id"], "not_started")  # Default fallback
        }
        for schedule in schedules
    ]

    return render(request, "app1/select_schedule_2.html", {"progress": progress})

from django.shortcuts import render
from .models import Section, SectionStatus

def select_section(request, schedule_id):
    # Step 1: Get context from session
    user_id = request.session.get("user_id")
    section_ids = request.session.get("section_ids", [])
    select_dict = request.session.get("select_dict", {})
    regime_id = select_dict.get("regime_id")

    # Step 2: Get permitted sections for this schedule
    sections = Section.objects.filter(
        section_id__in=section_ids,
        schedule_id=schedule_id,
        schedule__regime_id=regime_id
    ).values("section_id", "section_name")

    # Step 3: Fetch any existing SectionStatus records
    section_id_list = [s["section_id"] for s in sections]
    existing_statuses = {
        status.section_id: status.get_status_display()
        for status in SectionStatus.objects.filter(
            user_id=user_id,
            regime_id=regime_id,
            section_id__in=section_id_list
        )
    }

    # Step 4: Ensure each section has a status (create if needed)
    progress = []
    for section in sections:
        section_id = section["section_id"]

        if section_id not in existing_statuses:
            SectionStatus.objects.create(
                user_id=user_id,
                regime_id=regime_id,
                section_id=section_id,
                status="not_started"
            )
            status_value = "not_started"
        else:
            status_value = existing_statuses[section_id]

        progress.append({
            "name": section["section_name"],
            "href": f"/summarise_selection/{schedule_id}/{section_id}/",
            "status": status_value
        })

    return render(request, "app1/select_section_2.html", {"progress": progress})

def summarise_selection(request, schedule_id, section_id):
    section_ids = request.session.get("section_ids", [])
    select_dict = request.session.get("select_dict", {})

    # Verify the section is one the user is permitted to access
    try:
        section = Section.objects.select_related("schedule").get(
            section_id=section_id,
            schedule_id=schedule_id,
            section_id__in=section_ids
        )
    except Section.DoesNotExist:
        return redirect("select_schedule")  # Or raise a 403 if needed

    # Extract schedule from related field
    schedule = section.schedule

    # Update select_dict with both schedule and section details
    select_dict.update({
        "schedule_id": schedule.schedule_id,
        "schedule_name": schedule.schedule_name,
        "section_id": section.section_id,
        "section_name": section.section_name,
        "section_type": section.section_type,
    })

    request.session["select_dict"] = select_dict
    request.session["previous_question_ids"] = request.session.get("question_ids", []) # Store previous questions before re-routing
    request.session.modified = True
    print(select_dict)

    return redirect("process_section")


