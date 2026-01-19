from django.contrib import admin
from django.urls import path
from portal import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('faculty-dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('upload-students/', views.upload_students, name='upload_students'),
    path('trigger-seating/', views.trigger_seating, name='trigger_seating'),
    path('allocate-seating/', views.allocate_seating, name='allocate_seating'),
    path('faculty/seating/', views.faculty_seating_view, name='faculty_seating'),
    path('faculty/marks/', views.faculty_add_marks, name='faculty_add_marks'),
    path('faculty/circulars/', views.faculty_circulars, name='faculty_circulars'),
    path('faculty/circulars/add/', views.faculty_add_circular, name='faculty_add_circular'),
    path('student/seating/', views.student_seating_view, name='student_seating'),
    path('student/marks/', views.student_marks_view, name='student_marks'),
    path('student/circulars/', views.student_circulars, name='student_circulars'),

]

