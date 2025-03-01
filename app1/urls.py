from django.urls import path
from .views import upload_sections, upload_questions, upload_routing, display_permissions, display_regimes, display_schedules, display_sections,display_routing,display_questions, select_regime, select_schedule, select_section, question_router, radio_view, text_view, checkbox_view, process_answer, completion_page, restart_process, user_login
from . import views

urlpatterns = [
    path('', views.user_login, name='user_login'),

    path('upload/sections/', upload_sections, name='upload_sections'),
    path('upload/questions/', upload_questions, name='upload_questions'),
    path('upload/routing/', upload_routing, name='upload_routing'),

    path('display/permissions/', display_permissions, name='display_permissions'),
    path('display/regimes/', display_regimes, name='display_regimes'),
    path('display/schedules/', display_schedules, name='display_schedules'),
    path('display/sections/', display_sections, name='display_sections'),
    path('display/routing/', display_routing, name='display_routing'),
    path('display/questions/', display_questions, name='display_questions'),


    path('select_regime/', select_regime, name='select_regime'),
    path('select_schedule/', select_schedule, name='select_schedule'),
    path('select_section/', select_section, name='select_section'),

    # Route that dynamically determines the correct view based on question type
    path("question/<str:question_id>/", question_router, name="question_router"),

    # Individual views for different question types
    path("question/<str:question_id>/radio/", radio_view, name="radio_view"),
    path("question/<str:question_id>/text/", text_view, name="text_view"),
    path("question/<str:question_id>/checkbox/", checkbox_view, name="checkbox_view"),

    path("process/<str:question_id>/", process_answer, name="process_answer"),

    path("completion/", completion_page, name="completion_page"),

    path("restart/", restart_process, name="restart_process"),
]
