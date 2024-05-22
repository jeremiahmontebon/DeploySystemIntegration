"""
URL configuration for attendancelist project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.conf import settings 
from django.conf.urls.static import static
from base import views

urlpatterns = [
    path('singup/', views.SignupPage, name='signup'),
    path('', views.LoginPage, name='login'),
    path('home/', views.HomePage, name='home'),
    path('logout/', views.LogoutPage, name='logout'),

    # USER SIDE
    path('studentList/', views.StudentListPage, name='studentList'),
    path('attendanceChecker/', views.AttendanceChecker, name='attendanceChecker'),
    path('take-attendance/', views.take_attendance, name='take_attendance'),
    path('clear_attendance/', views.clear_attendance, name='clear_attendance'),
    path('previousRecords/', views.previousRecord, name='previousRecords'),
    
    # ADMIN SIDE
    path('admin/', views.AdminPage, name='admin'),
    path('course/', views.AddCourseInformationPage, name='course'),
    path('course/<int:id>/delete/', views.DeleteCourseInformation, name='deleteCourseInformation'),
    path('studentInformation/', views.AddStudentInformationPage, name='studentInformation'),
    path('studentInformation/<int:id>/delete/', views.DeleteStudentInformation, name='deleteStudentInformation'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
