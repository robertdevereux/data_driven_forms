# core_home/views.py

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from app1.models import Permission, Regime, Section, Routing, Question

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

    # Check 3: all Sections must belong to a Schedule or Regime
    bad_sections = Section.objects.filter(schedule__isnull=True, regime__isnull=True)
    if bad_sections.exists():
        bad_section_names = [s.section_name for s in bad_sections[:5]]
        errors.append(
            f"{bad_sections.count()} sections have no schedule or regime: "
            + ", ".join(bad_section_names) + ("..." if bad_sections.count() > 5 else "")
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
        user_section_ids = list( # Note: the opening brackets also permit the separate line treatment below
            Permission.objects
            .filter(user_id=user_id)
            .values_list("section_id", flat=True)
            .distinct()
        )

        if user_section_ids:

            user_regimes_query = get_permitted_regimes(user_id)
            user_regimes_list = [
                {
                    "id": str(r.regime_id),
                    "name": r.regime_name,
                    # "dept": r.regime_id.split("_")[0], # example of dynamic optional field
                    # "type": "Benefits"                 # example of hardcoded optional field
                }
                for r in user_regimes_query
            ]

            # create select_dict with user_id
            request.session["select_dict"] = {"user_id": user_id}  # initialise a new select_dic
            request.session["user_regimes_list"] = user_regimes_list
            request.session["user_section_ids"] = user_section_ids
            request.session.modified = True

            return redirect("select_regime")
        else:
            message = "No such user_id with valid permissions"

    return render(request, "app1/login.html", {"message": message})

def select_regime(request):
    if request.method == "POST":
        regime_id = request.POST.get("selected_regime")
        user_regimes_list = request.session.get("user_regimes_list", [])
        user_regime_ids = [r["id"] for r in user_regimes_list]

        if not regime_id or regime_id not in user_regime_ids:
            return HttpResponse("Something that should be impossible has occurred in select_regime")

        # get name for selected_regime_id
        regime_name = next( #cycles through regime_list to find a match on id
            (r["name"] for r in user_regimes_list if r["id"] == regime_id),"Unknown Regime"
        )

        # Look in user_section_ids for those relating to regime_id
        user_section_ids = request.session.get('user_section_ids')  # all the sections the user can access
        section_ids = Section.objects.filter(
            section_id__in=user_section_ids
        ).filter(
            Q(schedule__regime_id=regime_id) | Q(regime_id=regime_id)
        )

        # store key parameters in session
        select_dict = request.session.get("select_dict", {})
        select_dict["regime_id"] = regime_id
        select_dict["regime_name"] = regime_name
        request.session["select_dict"] = select_dict
        request.session['section_ids'] = list(section_ids.values_list("section_id", flat=True))

        if section_ids.count() == 1:
            section = section_ids.first()  # if there is only one, then .first() gets it
            request.session["select_dict"]["section_id"] = section.section_id  # find first and only id
            request.session["select_dict"]["section_type"] = section.section_type  # find first and only type
            request.session["select_dict"]["schedule_id"] = ""

        request.session.modified = True

        return redirect(f"regime_{regime_id.lower()}:start")

    # On GET: just pull from session, no DB call
    user_regimes_list = request.session.get("user_regimes_list", {})
    return render(request, "app1/select_regime.html", {"regimes": user_regimes_list})

def get_permitted_regimes(user_id):
    # Get all permitted sections
    user_sections = Section.objects.filter(permission__user_id=user_id)

    # Directly linked regimes
    direct_ids = user_sections.filter(regime__isnull=False).values_list('regime__regime_id', flat=True)

    # Indirect via schedule
    indirect_ids = user_sections.filter(schedule__isnull=False).values_list('schedule__regime__regime_id', flat=True)

    # Combine and deduplicate
    all_ids = set(direct_ids).union(set(indirect_ids))

    # Return Regime queryset
    return Regime.objects.filter(regime_id__in=all_ids)