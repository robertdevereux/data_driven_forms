from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Schedule, Section, ScheduleStatus, SectionStatus

'''
def model_to_dict(model, unique_field):
    # unique field is a string; model is just the model name (not a string)
    return {
        obj[unique_field]: {k: v for k, v in obj.items() if k != unique_field}
        for obj in model.objects.values()
    }
'''

def select_schedule(request):

    user_id = request.session.get("select_dict", {}).get("user_id")
    regime_id = request.session.get("select_dict", {}).get("regime_id")
    regime_name = request.session.get("select_dict", {}).get("regime_name")
    section_ids = request.session.get("section_ids", [])

    # Get schedules the user can access under this regime
    schedule_ids = (
        Section.objects.filter(section_id__in=section_ids, schedule__regime_id=regime_id)
        .values_list("schedule_id", flat=True)
        .distinct()
    )
    print("B: ",schedule_ids)
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
            "href": reverse("select_section", kwargs={"schedule_id": schedule["schedule_id"]}),
            "status": schedule_statuses.get(schedule["schedule_id"], "not_started")
        }
        for schedule in schedules
    ]

    return render(request, "app1/select_schedule_2.html", {"progress": progress, 'regime_name':regime_name})

def select_section(request, schedule_id=None):

    # Step 1: Get context from session
    user_id = request.session.get("select_dict", {}).get("user_id")
    regime_id = request.session.get("select_dict", {}).get("regime_id")
    regime_name = request.session.get("select_dict", {}).get("regime_name")
    section_ids = request.session.get("section_ids", [])

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
            "href": reverse("summarise_selection", kwargs={
                "schedule_id": schedule_id,
                "section_id": section_id
            }),
            "status": status_value
        })

    return render(request, "app1/select_section_2.html", {"progress": progress,'regime_name':regime_name})

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


