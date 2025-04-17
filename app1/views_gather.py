import csv, json, bleach
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.views.decorators.http import require_POST
from django.urls import reverse

from django.contrib import messages
from urllib.parse import urlencode
from core_home.views import end_url
from .models import Permission, Regime, Schedule, Section, Routing, Question, AnswerBasic, AnswerTable, ScheduleStatus, SectionStatus

ALLOWED_TAGS = ["b", "i", "u", "strong", "em", "h1", "h2", "h3", "p", "ul", "ol", "li", "br"]

def process_section(request):
    select_dict = request.session.get('select_dict')
    section_id = select_dict['section_id']

    # === 1. Get full routing data and store it ===
    routing_data = list(
        Routing.objects.filter(section_id=section_id)
        .order_by('order_in_section')
        .values()
    )
    request.session["routing_table"] = routing_data

    # === 2. Extract ordered list of unique question_ids from routing ===
    seen = set()
    question_ids = []
    for route in routing_data:
        qid = route["current_question"]
        if qid not in seen:
            question_ids.append(qid)
            seen.add(qid)

    # === 3. Fetch corresponding questions ===
    questions = Question.objects.filter(question_id__in=question_ids)

    # === 4. Build and store question lookup table ===
    request.session["question_table"] = {
        str(q.question_id): {
            "text": q.question_text,
            "guidance": q.guidance,
            "hint": q.hint,
            "question_type": q.question_type,
            "options": q.options if q.options else "",
        }
        for q in questions
    }

    # === 5. Initialise session state ===
    first_question_id = question_ids[0]
    select_dict['first_question_id'] = first_question_id
    request.session["asked_ids"] = [first_question_id]
    request.session["select_dict"] = select_dict
    request.session.modified = True

    # === 6. Handle section type ===
    if select_dict['section_type'] == 0:
        # Classic section – prepopulate answers from DB
        basic_answers = {
            str(a.question_id): a.answer
            for a in AnswerBasic.objects.filter(
                user_id=select_dict["user_id"],
                regime_id=select_dict["regime_id"],
                question_id__in=question_ids
            )
        }
        request.session["basic_answers"] = basic_answers
        return redirect("question_router", question_id=first_question_id)

    else:
        # Table section logic unchanged
        user_id = select_dict["user_id"]
        regime_id = select_dict["regime_id"]

        try:
            answer_record = AnswerTable.objects.get(
                user_id=user_id,
                regime_id=regime_id,
                question_id=section_id
            )
            record_count = len(answer_record.answer)
        except AnswerTable.DoesNotExist:
            record_count = 0

        select_dict["records"] = record_count
        request.session["select_dict"] = select_dict
        request.session["table_row"] = {}
        request.session.modified = True

        # Get summary context
        summary = get_table_summary_context(user_id, section_id)

        return render(request, "app1/table_summary.html", {
            "name": select_dict["section_name"],
            "first_question": first_question_id,
            **summary  # expands to 'records', 'summary_totals'
        })

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

        # collect the user response for question_id in the right format (as per question_type)
        question_data = request.session["question_table"].get(str(question_id))
        if question_data["question_type"].lower() == "checkbox":
            user_response = request.POST.getlist("question")
        else:
            user_response = request.POST.get("question", "").strip()

        # === Get routing info and asked_ids ===
        routing_table = request.session.get("routing_table", [])
        asked_ids = request.session.get("asked_ids", [])
        ordered_qids = list(dict.fromkeys(
            route["current_question"] for route in routing_table
        ))

        # === Trim asked_ids up to this question, based on routing order ===
        if question_id in ordered_qids:
            index = ordered_qids.index(question_id)
            new_asked_ids = ordered_qids[:index + 1]
        else:
            new_asked_ids = asked_ids + [question_id]  # fallback

        # === Store the current answer in session ===
        section_type = request.session.get("select_dict", {}).get("section_type")
        if section_type == 0:
            answers = request.session.get("basic_answers", {})
            answers[question_id] = user_response
            request.session["basic_answers"] = answers
        else:
            table_row = request.session.get("table_row", {})
            table_row[question_id] = user_response
            request.session["table_row"] = table_row

        request.session["asked_ids"] = new_asked_ids
        request.session.modified = True

        # === Determine next question via routing logic ===
        next_question_id = None
        for route in routing_table:
            if route["current_question"] == str(question_id):
                if route["answer_value"]:
                    allowed = [val.strip().lower() for val in route["answer_value"].split(";")]
                    if isinstance(user_response, list):
                        match = any(val.lower() in allowed for val in user_response)
                    else:
                        match = user_response.lower() in allowed
                    if match:
                        next_question_id = route["next_question"]
                        break
                else:
                    next_question_id = route["next_question"]

        # === If END, go to review ===
        if next_question_id == "END":
            return redirect("review_section")

        assert next_question_id is not None, f"No routing found from {question_id} with answer {user_response}"

        # === Append next question if not already in path ===
        if next_question_id not in new_asked_ids:
            new_asked_ids.append(next_question_id)
            request.session["asked_ids"] = new_asked_ids
            request.session.modified = True

        return redirect("question_router", question_id=next_question_id)

    # Fallback for GET
    return redirect("question_router", question_id=question_id)

def review_section(request):
    select_dict = request.session.get("select_dict", {})
    section_type = select_dict.get("section_type")
    asked_ids = request.session.get("asked_ids", [])

    # Load questions used in this section
    questions = Question.objects.filter(
        question_id__in=asked_ids
    ).in_bulk(field_name="question_id")

    # === Prepare answers based on section type ===
    rows = []

    if section_type == 0:
        # === Classic Section ===
        session_answers = request.session.get("basic_answers", {})

        for qid in asked_ids:
            question = questions.get(qid)
            raw_answer = session_answers.get(qid)
            display_answer = ", ".join(raw_answer) if isinstance(raw_answer, list) else raw_answer or "[No Answer]"

            rows.append({
                "question_id": qid,
                "question": question.question_text if question else "[Unknown Question]",
                "answer": display_answer
            })

    else:
        # === Table Section ===
        latest_row = request.session.get("table_row", {})

        for qid in asked_ids:
            question = questions.get(qid)
            raw_answer = latest_row.get(qid)
            display_answer = ", ".join(raw_answer) if isinstance(raw_answer, list) else raw_answer or "[No Answer]"

            rows.append({
                "question_id": qid,
                "question": question.question_text if question else "[Unknown Question]",
                "answer": display_answer
            })

    # Route to confirm_section to commit answers to DB
    context={}
    context['asked_ids'] = asked_ids
    if section_type==0:
        context['section_answers'] = session_answers
    confirm_url = reverse("confirm_section")
    return render(request, "app1/review_section.html", {
        "rows": rows,
        "confirm_url": confirm_url,
        "context":context
    })

#@require_POST
def confirm_section(request):

    select_dict = request.session["select_dict"]
    section_type = select_dict["section_type"]
    section_id = select_dict["section_id"]
    regime_id = select_dict["regime_id"]
    user_id = select_dict["user_id"]
    schedule_id = select_dict.get("schedule_id")  # different cos might not be schedule...
    old_record_count = select_dict.get("records")  # different cos might not be records...

    # === Classic Section: write individual answers ===
    if section_type == 0:
        answers = request.session.get("basic_answers", {})
        asked_ids = request.session.get("asked_ids", [])
        # 💡 Prune session answers down to asked_ids only
        answers = {qid: answers[qid] for qid in asked_ids if qid in answers}

        # Delete any answers previously saved to DB which no longer apply (eg cos user revisited and took shorter route)
        AnswerBasic.objects.filter(
            user_id=user_id,
            regime_id=regime_id,
            question_id__in=AnswerBasic.objects.filter(
                user_id=user_id,
                regime_id=regime_id
            ).exclude(question_id__in=asked_ids).values_list("question_id", flat=True)
        ).delete()

        for question_id, value in answers.items():
            AnswerBasic.objects.update_or_create(
                user_id=user_id,
                regime_id=regime_id,
                question_id=question_id,
                defaults={"answer": value}
            )

        # ✅ Mark section as complete (if classic)
        SectionStatus.objects.update_or_create(
            user_id=user_id,
            regime_id=regime_id,
            section_id=section_id,
            defaults={"status": "complete"}
        )

        # 📌 Update schedule status if relevant (if classic)
        if schedule_id:
            update_schedule_status(user_id, regime_id, schedule_id)

        a=continue_url(request)
        return redirect(a)

    # === Table Section: append full row to AnswerTable ===
    else:
        row = request.session.get("table_row", {})
        if row:
            answer_table, _ = AnswerTable.objects.get_or_create(
                user_id=user_id,
                regime_id=regime_id,
                question_id=section_id,
                defaults={"answer": []}
            )
            answer_table.answer.append(row)
            answer_table.save(update_fields=["answer"])

            # Update record count in session; reinitialise table_row
            new_record_count = old_record_count + 1
            select_dict["records"] = new_record_count
            request.session["select_dict"] = select_dict
            request.session["table_row"] = {}
            request.session.modified = True

            summary = get_table_summary_context(user_id, section_id)

            return render(request, "app1/table_summary.html", {
                "name": select_dict["section_name"],
                "first_question": select_dict["first_question_id"],
                **summary
            })

        else:
            # No row data found (unexpected)
            messages.warning(request, "No data to save. Please complete a table row first.")
            return redirect("process_section")

def continue_url(request):
    select_dict = request.session.get('select_dict')
    print("sch count=",select_dict['schedule_count'],"sec count=",select_dict['section_count'])
    if select_dict['section_count'] == 1:
        return 'regime_'+select_dict['regime_id'].lower()+":start"
    elif select_dict['schedule_count'] == 0:
        return reverse("select_section")
    else:
        return reverse("select_section", kwargs={"schedule_id": select_dict['schedule_id']})

def count_and_sum(user_id, section_id, target_qids):
    """
    Returns the number of records and, optionally, column totals for a user's table section.

    Args:
        user_id (str): The user's ID.
        section_id (str): The ID of the table section.
        target_qids (list[str]): List of question IDs to total.
                                 If an empty list is passed, no totals will be computed.

    Returns:
        tuple: (record_count, totals_list), where:
            - record_count (int): Number of records (rows) stored.
            - totals_list (list[float]): Totals per question ID (same order as target_qids),
                                         or an empty list if target_qids is empty.
    """
    try:
        entry = AnswerTable.objects.get(user_id=user_id, question_id=section_id)
        rows = entry.answer  # List of row dicts
    except AnswerTable.DoesNotExist:
        return 0, [0 for _ in target_qids]  # No data = 0 records, 0s for each column

    record_count = len(rows)

    # If no question IDs to total, return just the count and empty totals
    if not target_qids:
        return record_count, []

    totals = {qid: 0 for qid in target_qids}

    for row in rows:
        for qid in target_qids:
            value = row.get(qid)
            try:
                totals[qid] += float(value)
            except (TypeError, ValueError):
                pass  # Skip invalid or missing values

    totals_list = [totals[qid] for qid in target_qids]
    return record_count, totals_list


def get_table_summary_context(user_id, section_id):
    # Get record count + totals (only for totalled=1 fields)
    total_qids = list(Routing.objects.filter(
        section_id=section_id,
        totalled=1
    ).values_list("current_question", flat=True))

    record_count, totals = count_and_sum(user_id, section_id, total_qids)

    # Get labels
    questions = Question.objects.filter(question_id__in=total_qids).in_bulk(field_name="question_id")
    question_texts = [questions[qid].question_text for qid in total_qids if qid in questions]

    # Zip for template use
    summary_totals = list(zip(question_texts, totals))

    return {
        "records": record_count,
        "summary_totals": summary_totals
    }
