import csv, json, bleach
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from app1.models import AnswerBasic, AnswerTable, Question

ALLOWED_TAGS = ["b", "i", "u", "strong", "em", "h1", "h2", "h3", "p", "ul", "ol", "li", "br"]

def task_list(request):
    progress=[{'name':'Task 1', 'hint':'some hint', 'status':'Not started'}]
    return render(request, "app1/task_list.html", {"progress": progress})

def screen(request, question_id):
    question = request.session["question_table"].get(str(question_id))
    question_type = question["question_type"].lower()
    html_name = f"app1/template_{question_type}.html"

    select_dict = request.session.get("select_dict", {})
    section_type = select_dict.get("section_type")
    regime_name = select_dict.get("regime_name")

    context = {
        "regime_name": regime_name,
        "question_id": question_id,
        "question_text": question["text"],
        "guidance": bleach.clean(question["guidance"], tags=ALLOWED_TAGS) if question.get("guidance") else "",
        "hint": bleach.clean(question["hint"], tags=ALLOWED_TAGS) if question.get("hint") else "",
        "options": [opt.strip() for opt in question.get("options", "").split(";") if opt.strip()],
    }

    if section_type == 0:
        # Classic: pre-populate with answers in session["basic_answers"]
        session_answers = request.session.get("basic_answers", {})
        previous = session_answers.get(question_id)
        context['section_answers']=session_answers
    else:
        # Table: pre-populate with answers in  session["table_row"]
        table_row = request.session.get("table_row", {})
        previous = table_row.get(question_id)
        context['section_answers']=table_row

    if question_type == "checkbox": # Adjust per question type
        context["previous_answers"] = previous if isinstance(previous, list) else []
    else:
        context["previous_answer"] = previous if previous else ""

    context['asked_ids']=request.session.get("asked_ids")
    return render(request, html_name, context)

def table_details(request):
    select_dict = request.session.get("select_dict", {})
    section_id = select_dict.get("section_id")
    user_id = select_dict.get("user_id")
    regime_id = select_dict.get("regime_id")

    # Fetch stored rows
    try:
        answer_obj = AnswerTable.objects.get(
            user_id=user_id,
            regime_id=regime_id,
            question_id=section_id
        )
        records = answer_obj.answer  # List of dicts
    except AnswerTable.DoesNotExist:
        records = []

    # Get all question IDs used across rows (preserves order of first appearance)
    question_ids = []
    seen = set()
    for row in records:
        for qid in row:
            if qid not in seen:
                question_ids.append(qid)
                seen.add(qid)

    # Load question metadata
    questions = Question.objects.filter(question_id__in=question_ids).in_bulk(field_name="question_id")

    # Prepare display headers (question text) and row values
    headers = [questions[qid].question_text if qid in questions else qid for qid in question_ids]

    table_rows = []
    for row in records:
        row_values = []
        for qid in question_ids:
            val = row.get(qid)
            if isinstance(val, list):
                val = ", ".join(val)
            row_values.append(val or "-")
        table_rows.append(row_values)

    return render(request, "app1/table_details.html", {
        "section_id": section_id,
        "section_name": select_dict.get("section_name"),
        "table": {
            "headers": headers,
            "rows": table_rows
        },
        "has_records": bool(table_rows)
    })

def delete_table_record(request, section_id, record_index):
    select_dict = request.session.get("select_dict", {})
    user_id = select_dict.get("user_id")
    regime_id = select_dict.get("regime_id")

    try:
        answer_obj = AnswerTable.objects.get(
            user_id=user_id,
            regime_id=regime_id,
            question_id=section_id
        )
        records = answer_obj.answer
    except AnswerTable.DoesNotExist:
        records = []

    # Safely delete the record if index is valid
    if 0 <= record_index < len(records):
        del records[record_index]
        # Save back updated records
        AnswerTable.objects.update_or_create(
            user_id=user_id,
            regime_id=regime_id,
            question_id=section_id,
            defaults={"answer": records}
        )

    # Redirect back to the table details page
    return redirect(reverse("table_details"))


