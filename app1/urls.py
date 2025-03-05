from django.urls import path
from .views import consistency_check, user_login, select_regime, select_schedule, select_section, question_router, radio_view, text_view, textarea_view, checkbox_view, process_answer, completion_page, restart_process
from .views_data import upload_regimes, upload_schedules, upload_sections, upload_routing, upload_questions, upload_permissions, display_regimes, display_schedules, display_sections,display_routing,display_questions, display_permissions
from . import views

urlpatterns = [

    path('', views.consistency_check, name='consistency_check'),
    path('user_login', views.user_login, name='user_login'),

    path('upload/regimes/', upload_regimes, name='upload_regimes'),
    path('upload/schedules/', upload_schedules, name='upload_schedules'),
    path('upload/sections/', upload_sections, name='upload_sections'),
    path('upload/routing/', upload_routing, name='upload_routing'),
    path('upload/questions/', upload_questions, name='upload_questions'),
    path('upload/permissions/', upload_permissions, name='upload_permissions'),

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
    path("question/<str:question_id>/textarea/", textarea_view, name="textarea_view"),
    path("question/<str:question_id>/checkbox/", checkbox_view, name="checkbox_view"),

    path("process/<str:question_id>/", process_answer, name="process_answer"),

    path("completion/", completion_page, name="completion_page"),

    path("restart/", restart_process, name="restart_process"),
]
