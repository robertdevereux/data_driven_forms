import csv, json, bleach
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from urllib.parse import urlencode
from .models import Question, Routing, Section, Schedule, Regime, Permission

def user_login(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id").strip()
        if not user_id:
            messages.error(request, "Please enter a valid user ID.")
            return redirect("user_login")

        request.session["user_id"] = user_id
        permissions = Permission.objects.filter(user_id=user_id)
        request.session["permissions"] = list(permissions.values())

        return redirect("select_regime")

    return render(request, "app1/user.html")


def select_regime(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("user_login")

    permissions = request.session.get("permissions", [])
    print(f"DEBUG: Permissions from session: {permissions}")  # Check session data

    regime_ids = {perm["regime_id"] for perm in permissions if perm.get("regime_id")}
    print(f"DEBUG: Extracted regime IDs: {regime_ids}")  # Check extracted IDs

    regimes = Regime.objects.filter(regime_id__in=regime_ids)
    print(f"DEBUG: Retrieved regimes: {[r.regime_name for r in regimes]}")  # Check query results

    if request.method == "POST":
        regime_id = request.POST.get("regime_id")
        if regime_id in regime_ids:
            request.session["regime_id"] = regime_id
            return redirect("select_schedule")
        messages.error(request, "Invalid regime selection.")

    return render(request, "app1/regime.html", {"regimes": regimes})


def select_schedule(request):
    return HttpResponse("Placeholder for selecting a schedule.")


def select_section(request):
    return HttpResponse("Placeholder for selecting a section.")


def question_router(request, question_id):
    return HttpResponse(f"Routing to question {question_id}.")


def radio_view(request, question_id):
    return HttpResponse(f"Displaying radio question {question_id}.")


def text_view(request, question_id):
    return HttpResponse(f"Displaying text question {question_id}.")


def checkbox_view(request, question_id):
    return HttpResponse(f"Displaying checkbox question {question_id}.")


def process_answer(request, question_id):
    return HttpResponse(f"Processing answer for {question_id}.")


def completion_page(request):
    return HttpResponse("Completion page placeholder.")


def restart_process(request):
    return HttpResponse("Restarting process.")