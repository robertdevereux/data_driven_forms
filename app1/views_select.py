from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Schedule, Section, ScheduleStatus, SectionStatus

def select_schedule(request):

    # Get schedules the user can access under this regime
    select_dict=request.session.get("select_dict")
    regime_id = select_dict["regime_id"]
    section_ids = request.session.get("section_ids", []) # all sections in selected regime that user can access
    schedule_ids = (
        Section.objects.filter(section_id__in=section_ids, schedule__regime_id=regime_id)
        .values_list("schedule_id", flat=True)
        .distinct()
    )
    schedules = Schedule.objects.filter(schedule_id__in=schedule_ids).values("schedule_id", "schedule_name")

    # Get schedule completion statuses, and populate list of schedules (progress) for html
    user_id = select_dict["user_id"]
    schedule_statuses = {
        status.schedule_id: status.get_status_display()
        for status in ScheduleStatus.objects.filter(user_id=user_id, regime_id=regime_id)
    }
    progress = [
        {
            "schedule_id": schedule["schedule_id"],
            "name": schedule["schedule_name"],
            "href": reverse("record_schedule_choice", kwargs={"schedule_id": schedule["schedule_id"]}),
            "status": schedule_statuses.get(schedule["schedule_id"], "Not started")
        }
        for schedule in schedules
    ]

    # Define the url to use when all schedules complete, get regime name, and render select_schedule html
    home_name = f"regime_{regime_id.lower()}:start"
    url_home = reverse(home_name)
    regime_name = select_dict["regime_name"]
    return render(request, "app1/select_schedule_2.html", {"progress": progress, 'regime_name':regime_name, 'url_home':url_home})

def record_schedule_choice(request, schedule_id):
    select_dict = request.session.get("select_dict", {})
    select_dict["schedule_id"] = schedule_id
    select_dict["section_id"] = ""  # clear any pre-existing downstream values, as starting new schedule
    request.session["select_dict"] = select_dict
    request.session.modified = True

    return redirect("select_section", schedule_id=schedule_id)

def select_section(request, schedule_id=None):

    # Flush any previous completed section data
    for key in ["basic_answers", "table_row", "asked_ids", "routing_table", "question_table"]:
        request.session.pop(key, None)
    for subkey in ["first_question_id", "section_id", "section_name", "section_type"]:
        request.session.get("select_dict", {}).pop(subkey, None)
    request.session.modified = True

    # Get permitted sections for this schedule
    select_dict=request.session.get("select_dict")
    regime_id = select_dict["regime_id"]
    section_ids = request.session.get("section_ids")
    sections = Section.objects.filter(
        section_id__in=section_ids,
        schedule_id=schedule_id,
        schedule__regime_id=regime_id
    ).values("section_id", "section_name")

    # Fetch any existing SectionStatus records
    user_id=select_dict['user_id']
    section_id_list = [s["section_id"] for s in sections]
    existing_statuses = {
        status.section_id: status.get_status_display()
        for status in SectionStatus.objects.filter(
            user_id=user_id,
            regime_id=regime_id,
            section_id__in=section_id_list
        )
    }

    # Ensure each section has a status (create if needed), and create list of all sections for html
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
            "section_id": section_id,
            "href": reverse("record_section_choice", kwargs={"section_id": section_id}),
            "status": status_value
        })

    # define the url to use when all sections complete, get regime name, and render select_section html
    if select_dict['schedule_count'] == 0:
        url_home =  'regime_' + select_dict['regime_id'].lower() + ":start"
    else:
        url_home =  reverse("select_schedule")
    regime_name = select_dict["regime_name"]
    return render(request, "app1/select_section_2.html", {"progress": progress,'regime_name':regime_name, 'url_home':url_home})

def record_section_choice(request, section_id):
    section_ids = request.session.get("section_ids", [])
    select_dict = request.session.get("select_dict", {})

    # Safety check: make sure user can access this section
    try:
        section = Section.objects.get(
            section_id=section_id,
            section_id__in=section_ids
        )
    except Section.DoesNotExist:
        return redirect("select_schedule")  # or another safe fallback

    # Update only section-specific values
    select_dict.update({
        "section_id": section.section_id,
        "section_name": section.section_name,
        "section_type": section.section_type,
    })

    request.session["select_dict"] = select_dict
    request.session["previous_question_ids"] = request.session.get("question_ids", [])
    request.session.modified = True

    return redirect("process_section")



