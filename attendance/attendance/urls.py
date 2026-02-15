from django.urls import path
from . import views, api_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('register/choice/', views.register_choice, name='register_choice'),
    path('register/student/', views.register_student, name='register_student'),
    path('register/teacher/', views.register_teacher, name='register_teacher'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('my-attendance/', views.my_attendance, name='my_attendance'),
    path('class/<int:class_id>/', views.class_students, name='class_students'),
    path('class/<int:class_id>/mark/', views.mark_attendance, name='mark_attendance'),
    path('class/<int:class_id>/report/', views.attendance_report, name='attendance_report'),
    path('class/<int:class_id>/report/<str:date_str>/', views.attendance_report, name='attendance_report_date'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    
    path('api/attendance/', api_views.api_attendance_list, name='api_attendance_list'),
    path('api/attendance/mark/', api_views.api_mark_attendance, name='api_mark_attendance'),
    path('api/attendance/<int:attendance_id>/', api_views.api_attendance_detail, name='api_attendance_detail'),
]

