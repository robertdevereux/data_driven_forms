from django.urls import path
from .views import restart_process, assign_routing_order2
from .views_data import load_dummy_data, upload_regimes, upload_schedules, upload_sections, upload_routing, upload_questions, upload_permissions, new_regime, new_schedule, new_section, display_regimes, display_schedules, display_sections,display_routing,display_questions, display_permissions, display_answer_basic
from .views_select import select_schedule, select_section, record_schedule_choice, record_section_choice
from .views_gather import process_section, question_router, process_answer, review_section, confirm_section
from .views_screens import screen, task_list, table_details, delete_table_record
from . import views

urlpatterns = [

    # from views
    path("restart/", restart_process, name="restart_process"),
    path('assign_routing_order/', assign_routing_order2, name='assign_routing_order'),

    # from views_data: upload files
    path('load_dummy_data/', load_dummy_data, name='load_dummy_data'),
    path('upload/regimes/', upload_regimes, name='upload_regimes'),
    path('upload/schedules/', upload_schedules, name='upload_schedules'),
    path('upload/sections/', upload_sections, name='upload_sections'),
    path('upload/routing/', upload_routing, name='upload_routing'),
    path('upload/questions/', upload_questions, name='upload_questions'),
    path('upload/permissions/', upload_permissions, name='upload_permissions'),

    # from views_data: enter data to define new elements
    path('new/regime/', new_regime, name='new_regime'),
    path('new/schedule/', new_schedule, name='new_schedule'),
    path('new/section/', new_section, name='new_section'),

    # from views_data: display data
    path('display/permissions/', display_permissions, name='display_permissions'),
    path('display/regimes/', display_regimes, name='display_regimes'),
    path('display/schedules/', display_schedules, name='display_schedules'),
    path('display/sections/', display_sections, name='display_sections'),
    path('display/routing/', display_routing, name='display_routing'),
    path('display/questions/', display_questions, name='display_questions'),
    path('display/answer_basic/', display_answer_basic, name='display_answer_basic'),

    # from views_select
    path("select_schedule/", select_schedule, name="select_schedule"),
    path("select_section/<str:schedule_id>/", select_section, name="select_section"), # with schedule
    path("select_section/", select_section, name="select_section"),  # no schedule_id = simple regime
    #path("summarise_selection/<str:schedule_id>/<str:section_id>/", summarise_selection, name="summarise_selection"),
    path("record-section/<str:section_id>/", record_section_choice, name="record_section_choice"),
    path("record-schedule/<str:schedule_id>/", record_schedule_choice, name="record_schedule_choice"),


    # from views_gather
    path("process_section/", process_section, name="process_section"),
    path("question/<str:question_id>/", question_router, name="question_router"),
    path("process/<str:question_id>/", process_answer, name="process_answer"),
    path("review_section/", review_section, name="review_section"),
    path("confirm_section/", confirm_section, name="confirm_section"),

    # from views_screens
    path("task_list/", task_list, name="task_list"),
    path("screen/<str:question_id>/", screen, name="screen"),
    path("table_details",table_details,name="table_details"),
    path('section/<str:section_id>/delete/<int:record_index>/', delete_table_record, name='delete_table_record'),



]
