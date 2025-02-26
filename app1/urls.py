from django.urls import path
from .views import upload_screen_questions, upload_screen_routing, display_screen_questions, display_screen_routing, select_service, screen1, question_router, radio_view, text_view, checkbox_view, process_answer, completion_page, restart_process
from . import views

urlpatterns = [
    path('', views.app1_home),
    path('p2/', views.p2),
    path('upload/questions/', upload_screen_questions, name='upload_screen_questions'),
    path('upload/routing/', upload_screen_routing, name='upload_screen_routing'),
    path('display/questions/', display_screen_questions, name='display_screen_questions'),
    path('display/routing/', display_screen_routing, name='display_screen_routing'),
    path('select_service/', select_service, name='select_service'),
    path('screen1/', screen1, name='screen1'),

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