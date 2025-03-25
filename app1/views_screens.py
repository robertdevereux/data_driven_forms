import csv, json, bleach
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from app1.models import AnswerBasic

ALLOWED_TAGS = ["b", "i", "u", "strong", "em", "h1", "h2", "h3", "p", "ul", "ol", "li", "br"]

def task_list(request):
    progress=[{'name':'Task 1', 'hint':'some hint', 'status':'Not started'}]
    return render(request, "app1/task_list.html", {"progress": progress})

def screen(request, question_id):
    question = request.session["question_table"].get(str(question_id))
    if not question:
        return HttpResponseNotFound(f"Question data for question id {question_id} not found in session.")

    question_type = question["question_type"].lower()
    html_name = f"app1/template_{question_type}.html"
    user_id = request.session.get("user_id")
    regime_name = request.session.get("select_dict", {}).get("regime_name")

    # Base context
    context = {
        "regime_name":regime_name,
        "question_id": question_id,
        "question_text": question["text"],
        "guidance": bleach.clean(question["guidance"], tags=ALLOWED_TAGS) if question.get("guidance") else "",
        "hint": bleach.clean(question["hint"], tags=ALLOWED_TAGS) if question.get("hint") else "",
        "options": [opt.strip() for opt in question["options"].split(";")] if question.get("options") else [],
    }

    # Attach previous answer(s) depending on question_type
    if question_type == "checkbox":
        previous_entry = AnswerBasic.objects.filter(user_id=user_id, question_id=question_id).order_by("-created_at").first()
        context["previous_answers"] = previous_entry.get_answer() if previous_entry else []

    elif question_type in ["radio", "text", "textarea", "table"]:
        previous_answer = AnswerBasic.objects.filter(user_id=user_id, question_id=question_id).order_by("-created_at").values_list("answer", flat=True).first()
        context["previous_answer"] = previous_answer.strip() if previous_answer else ""

    return render(request, html_name, context)

