import csv, json, bleach
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.contrib import messages
from urllib.parse import urlencode
from .models import Permission, Regime, Schedule, Section, Routing, Question, AnswerBasic, AnswerTable, ScheduleStatus, SectionStatus

ALLOWED_TAGS = ["b", "i", "u", "strong", "em", "h1", "h2", "h3", "p", "ul", "ol", "li", "br"]

def process_section(request):
    select_dict = request.session.get('select_dict')
    section_id = select_dict['section_id']

    # Get routing data
    routing_data = list(Routing.objects.filter(section_id=section_id).values())
    request.session["routing_table"] = routing_data

    # Get all questions used in routing
    question_ids = {route["current_question"] for route in routing_data}
    questions = Question.objects.filter(question_id__in=question_ids)

    # Store question lookup table
    request.session["question_table"] = {
        str(question.question_id): {
            "text": question.question_text,
            "guidance": question.guidance,
            "hint": question.hint,
            "question_type": question.question_type,
            "options": question.options if question.options else "",
        }
        for question in questions
    }

    # Initialise asked_ids with the first question in the routing table
    first_question_id = routing_data[0]["current_question"]
    request.session["asked_ids"] = [first_question_id]
    request.session.modified = True

    # Redirect to first question (or table summary)
    if select_dict['section_type'] == 0:
        return redirect("question_router", question_id=first_question_id)
    else:
        selected_section = request.session.get('selected_section')
        return render(request, "app1/table_summary.html", {"selected_section": selected_section})

def question_router(request, question_id):
    question = request.session["question_table"].get(str(question_id))

    if not question:
        return HttpResponseNotFound(f"Question data for question id {question_id} not found in session.")

    # Use `question_type` to determine the correct screen type
    if question["question_type"].lower() == "radio":
        return redirect("screen", question_id=question_id)
        #return redirect("screen", question_id=question_id)
    elif question["question_type"].lower() == "text":
        return redirect("screen", question_id=question_id)
        #return redirect("screen", question_id=question_id)
    elif question["question_type"].lower() == "textarea":
        return redirect("screen", question_id=question_id)
    elif question["question_type"].lower() == "checkbox":
        return redirect("screen", question_id=question_id)
    elif question["question_type"].lower() == "table":
        return redirect("screen", question_id=question_id)
    else:
        print(f"Unknown question type for {question_id}: {question['question_type']}")
        return redirect("completion_page")  # Default fallback

def update_schedule_status(user_id, regime_id, schedule_id):

    section_statuses = SectionStatus.objects.filter(
        user_id=user_id, regime_id=regime_id, section_id__in=Section.objects.filter(schedule_id=schedule_id).values_list("section_id", flat=True)
    ).values_list("status", flat=True) # Get all sections within this schedule

    if not section_statuses or all(status == "not_started" for status in section_statuses): # Determine the overall schedule status
        new_status = "not_started"
    elif all(status == "complete" for status in section_statuses):
        new_status = "complete"
    else:
        new_status = "in_progress"

    ScheduleStatus.objects.update_or_create( # Update or create the schedule status
        user_id=user_id, regime_id=regime_id, schedule_id=schedule_id,
        defaults={"status": new_status}
    )

def process_answer(request, question_id):
    if request.method == "POST":

        # Retrieve question from session
        question_data = request.session["question_table"].get(str(question_id))
        if not question_data:
            return HttpResponseNotFound(f"Question data for question id {question_id} not found in session.")

        # Capture user input (single or multiple depending on type)
        if question_data["question_type"] == "Checkbox":
            user_response = request.POST.getlist("question")  # multiple values
            print("Captured user_response:", user_response, type(user_response))
        else:
            user_response = request.POST.get("question", "").strip()

        # Get session context
        select_dict = request.session.get("select_dict")
        print("In process_answer. select_dict=",select_dict)
        user_id = select_dict["user_id"]
        regime_id = select_dict["regime_id"]
        regime_name = select_dict["regime_name"]
        schedule_id = select_dict["schedule_id"]
        section_id = select_dict["section_id"]

        # Update asked_ids list
        asked_ids = request.session.get("asked_ids", [])
        if question_id in asked_ids:
            index = asked_ids.index(question_id)
            asked_ids = asked_ids[:index + 1]
        else:
            asked_ids.append(question_id)
        request.session["asked_ids"] = asked_ids

        # ✅ Save or update answer using set_answer()
        answer, _ = AnswerBasic.objects.get_or_create(
            user_id=user_id,
            regime_id=regime_id,
            question_id=question_id
        )
        answer.set_answer(user_response)  # Handles JSON if needed
        answer.save()
        print(f"Answer saved for {question_id}: {answer.answer}")

        # Determine next question from routing
        routing_table = request.session.get("routing_table", [])
        next_question_id = None
        for route in routing_table:
            if route["current_question"] == str(question_id):
                if route["answer_value"]:  # Conditional route
                    allowed_answers = [ans.strip().lower() for ans in route["answer_value"].split(";")]
                    if isinstance(user_response, list):
                        match = any(ans.lower() in allowed_answers for ans in user_response)
                    else:
                        match = user_response.lower() in allowed_answers
                    if match:
                        next_question_id = route["next_question"]
                        break
                else:
                    next_question_id = route["next_question"]

        # ✅ Handle END of section
        if next_question_id == "END":
            if select_dict["section_type"] == 0:
                SectionStatus.objects.update_or_create(
                    user_id=user_id,
                    regime_id=regime_id,
                    section_id=section_id,
                    defaults={"status": "complete"}
                )
                update_schedule_status(user_id, regime_id, schedule_id)
                return redirect("review_section")
            else:
                n = request.session.get("selected_section").get("records")
                request.session["selected_section"]["records"] = n + 1
                request.session.modified = True
                selected_section = request.session.get("selected_section")
                return render(request, "app1/table_summary.html", {"selected_section": selected_section})

        # Handle missing routing
        if not next_question_id:
            error_message = f"No valid next question found for '{question_id}' with answer '{user_response}'."
            print(error_message)
            return redirect(f"/app1/completion/?{urlencode({'error_message': error_message})}")

        # Append next question to asked_ids if not already present
        if next_question_id not in asked_ids:
            asked_ids.append(next_question_id)
            request.session["asked_ids"] = asked_ids
            request.session.modified = True

        return redirect("question_router", question_id=next_question_id)

    # Default fallback for GET requests
    return redirect("question_router", question_id=question_id)

def review_section(request):

    select_dict = request.session.get("select_dict")
    user_id = select_dict["user_id"]
    regime_id = select_dict["regime_id"]
    asked_ids = request.session.get("asked_ids", [])

    # Clean up obsolete answers (not in asked_ids)
    all_answered = AnswerBasic.objects.filter(
        user_id=user_id,
        regime_id=regime_id
    ).values_list("question_id", flat=True)

    obsolete_ids = set(all_answered) - set(asked_ids)
    if obsolete_ids:
        AnswerBasic.objects.filter(
            user_id=user_id,
            regime_id=regime_id,
            question_id__in=obsolete_ids
        ).delete()
        print("Deleted obsolete answers:", obsolete_ids)

    # Pull only current answers for asked questions
    answers = AnswerBasic.objects.filter(
        user_id=user_id,
        regime_id=regime_id,
        question_id__in=asked_ids
    )

    # Load questions
    questions = Question.objects.filter(
        question_id__in=asked_ids
    ).in_bulk(field_name="question_id")

    # Build row list in order
    rows = []
    for qid in asked_ids:
        question = questions.get(qid)
        answer_entry = next((a for a in answers if a.question_id == qid), None)

        if answer_entry:
            raw_answer = answer_entry.get_answer()
            # Format checkbox list as comma-separated, others as-is
            if isinstance(raw_answer, list):
                display_answer = ", ".join(raw_answer)
            else:
                display_answer = raw_answer
        else:
            display_answer = "[No Answer]"

        rows.append({
            "question_id": qid,
            "question": question.question_text if question else "[Unknown Question]",
            "answer": display_answer
        })

    return render(request, "app1/review_section.html", {
        "rows": rows,
        "confirm_button": True
    })

def completion_page(request):
    error_message = request.GET.get("error_message", "")  # Ensure error message is a string
    final_json = request.session.get("final_json")  # Retrieve stored JSON

    if not final_json:
        final_json = json.dumps({"message": "No responses recorded"}, indent=4)  # Default JSON if empty

    return render(request, "app1/completion.html", {
        "error_message": error_message,
        "final_json": final_json
    })
