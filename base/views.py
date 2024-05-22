from django.shortcuts import render, redirect,  get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Student, Course, Attendance
from django.conf import settings
from django.views.decorators.http import require_POST
from datetime import datetime
import pandas as pd
import re
import subprocess
import csv
import os
import logging
import json


# Create your views here.
@login_required(login_url='login')
def HomePage(request):
    return render (request, 'home.html')

def SignupPage(request):
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        # Email validation pattern
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

        if pass1 != pass2:
            return render(request, 'signup.html')
        elif len(pass1) < 8 or not any(char.isupper() for char in pass1):
            return render(request, 'signup.html')
        elif not email_pattern.match(email):
            return render(request, 'signup.html')
        else:
            user = User.objects.create_user(username, email, pass1)
            user.save()
            return redirect('login')
    else:
        error_message = None

    return render(request, 'signup.html', {'error_message': error_message})

def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        encrypted_password = request.POST.get('password')

        # Decrypt the password (for demonstration purposes only)
        decrypted_password = simple_decrypt(encrypted_password)

        user = authenticate(request, username=username, password=encrypted_password)

        if user is not None:
            login(request, user)
            if user.is_superuser:  # Check if the user is a superuser
                return redirect('admin')
            else:
                return redirect('home')
        else:
            error_message = 'Username or password is incorrect'
            return render(request, 'login.html', {'error_message': error_message})

    return render (request, 'login.html')

# decryption
def simple_decrypt(encrypted_password):
    decrypted = ''
    for char in encrypted_password:
        decrypted += chr(ord(char) - 5)
    return decrypted

def LogoutPage(request):
    logout(request)
    return redirect('login')

def AdminPage(request):
    return render(request, 'admin.html')

@login_required(login_url='login')
def AddCourseInformationPage(request):
    # Fetch all non-superuser users
    teachers = User.objects.filter(is_superuser=False)
    courses = Course.objects.all() 

    if request.method == 'POST':
        course_name = request.POST.get('course')
        teacher = request.POST.get('teacher')
        
        selected_teacher = User.objects.get(username=teacher)
        
        # Check if the course with the same name already exists
        if not Course.objects.filter(course_name=course_name).exists():
            # Create a new course object and save it to the database
            new_course = Course.objects.create(course_name=course_name, teacher=selected_teacher)

        # Fetch the list of courses to display in the table
        courses = Course.objects.all()
        
        return redirect('course')
    
    return render(request, 'course.html', {'teachers': teachers, 'courses': courses})

@login_required(login_url='login')
def AddStudentInformationPage(request):
    courses = Course.objects.all() 

    if request.method == 'POST':
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        face_image = request.FILES.get('face_image')
        course = request.POST.get('course')

        selected_course = Course.objects.get(course_name=course)

        # Check if a student with the same first and last names exists within the same course
        if not Student.objects.filter(first_name=first_name, last_name=last_name, course=selected_course).exists():
            # If no duplicate student found within the same course, create and save the student object
            student = Student(first_name=first_name, last_name=last_name, face_image=face_image, course=selected_course)
            student.save()

            # Save the image to the existing ImageAttendance folder within the FacialRecognition folder
            image_dir = os.path.join(settings.BASE_DIR, 'FacialRecognitionAttendance', 'ImageAttendance')
            image_path = os.path.join(image_dir, face_image.name)
            with open(image_path, 'wb') as f:
                for chunk in face_image.chunks():
                    f.write(chunk)

    # Fetch the list of students to display in the table
    students = Student.objects.all()

    return render(request, 'studentInformation.html', {'courses': courses, 'students': students})

@login_required(login_url='login')
def DeleteStudentInformation(request, id):
    try:
        student = get_object_or_404(Student, pk=id)
        
        # Construct the absolute file path
        image_path = os.path.join(settings.BASE_DIR, 'FacialRecognition', 'ImageAttendance', student.face_image.name)
        image_path = os.path.normpath(image_path)  # Normalize the file path

        if os.path.exists(image_path):
            os.remove(image_path)
            logging.info(f"Deleted image file: {image_path}")
        else:
            logging.warning(f"Image file not found at: {image_path}")

        student.delete()
        return JsonResponse({'message': 'Student deleted successfully'}, status=200)
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        logging.error(f"Error occurred while deleting student and image: {str(e)}")
        return JsonResponse({'error': 'An error occurred while deleting the student'}, status=500)
    
@login_required(login_url='login')
def DeleteCourseInformation(request, id):
    try:
        course = get_object_or_404(Course, pk=id)
        course.delete()
        return JsonResponse({'message': 'Course deleted successfully'}, status=200)
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Course not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@login_required(login_url='login')
def StudentListPage(request):
    current_user = request.user
    
    if not current_user.is_superuser:
        student_info = Student.objects.filter(course__teacher=current_user)
        courses = Course.objects.filter(teacher=current_user)
        return render(request, 'studentList.html', {'student_info': student_info, 'courses': courses})
    else:
        return HttpResponseForbidden("Access Denied: Only non-superuser teachers can access this page.")

def filter_attendance_by_date(request):
    selected_date = request.POST.get('selected_date')

    # Query records where date field equals selected_date
    records = Attendance.objects.filter(selected_date=selected_date).values('student_name', 'date', 'time')


    context = {
        'records': records,
    }

    return render(request, 'attendanceChecker.html', context)


@login_required(login_url='login')
def previousRecord(request):
    current_user = request.user
    courses = Course.objects.filter(teacher=current_user)
    if request.method == 'POST':
        selected_date = request.POST.get('selected_date')
        selected_course_name = request.POST.get('selected_course')

        # Get the Course object based on the selected_course name
        course = Course.objects.get(course_name=selected_course_name)

        # Filter Attendance records based on selected course_id and date
        attendance_records = Attendance.objects.filter(course_id=course.id, date=selected_date)

        # Pass the filtered records to the template
        context = {
            'attendance_records': attendance_records,
            'courses': courses,
            'selected_course_name': selected_course_name  # Pass the selected course name
        }
        return render(request, 'previousRecord.html', context)
    else:
        # Fetch all courses from the database
        # courses = Course.objects.all()

        # Pass the courses to the template
        context = {
            'courses': courses
        }
        return render(request, 'previousRecord.html', context)
            




@login_required(login_url='login')
def AttendanceChecker(request):
    current_user = request.user

    if not current_user.is_superuser:
        if request.method == 'POST':
            selected_course_name = request.POST.get('course')
            selected_course = Course.objects.get(course_name=selected_course_name)
            students = Student.objects.filter(course=selected_course)

            attendance_data = {}
            try:
                with open('FacialRecognitionAttendance/Attendance.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    # Processing each row in the CSV
                    for row in reader:
                        student_name, date, time = row
                        for student in students:
                            # Check if last_name of any student is in the student_name from the CSV
                            if student.last_name in student_name:
                                if student not in attendance_data:
                                    attendance_data[student] = []
                                attendance_data[student].append((date, time))

                                # Check if an attendance record already exists in the database for the same student, course, and date
                                existing_attendance = Attendance.objects.filter(
                                    student_name=student,
                                    course=selected_course,
                                    date=date
                                ).exists()
                                
                                if not existing_attendance:
                                    # Save attendance data to the database
                                    Attendance.objects.create(
                                        student_name=student,
                                        course=selected_course,
                                        date=date,
                                        time=time
                                    )
       
            except Exception as e:
                print("Error:", e)


            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string(selected_course, students, attendance_data)
                return JsonResponse({'html': html})
            
            return render(request, 'attendanceChecker.html', {'selected_course': selected_course, 'students': students, 'attendance_data': attendance_data})
        elif 'download_excel' in request.GET:
            selected_course_name = request.GET.get('course')
            selected_course = Course.objects.get(course_name=selected_course_name)
            students = Student.objects.filter(course=selected_course)

            attendance_data = []
            try:
                with open('FacialRecognitionAttendance/Attendance.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        student_name, date, time = row
                        for student in students:
                            if student.last_name in student_name:
                                attendance_data.append({
                                    'Student Name': f"{student.first_name} {student.last_name}",
                                    'Date': date,
                                    'Time': time
                                })
            except Exception as e:
                print("Error:", e)

            df = pd.DataFrame(attendance_data)
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename=Attendance_{selected_course_name}.xlsx'
            df.to_excel(response, index=False, engine='openpyxl')
            return response
        else:
            courses = Course.objects.filter(teacher=current_user)
            return render(request, 'attendanceChecker.html', {'courses': courses})
    else:
        return HttpResponseForbidden("Access Denied: Only non-superuser teachers can access this page.")


def render_to_string(selected_course, students, attendance_data):
    html = ""
    if students:
        html += f"<h3>Attendance Table for {selected_course.course_name}</h3>"
        html += "<table border='1'>"
        html += "<thead><tr><th>Student Name</th><th>Date</th><th>Time</th></tr></thead><tbody>"
        for student, attendance_records in attendance_data.items():
            html += f"<tr><td>{student.first_name} {student.last_name}</td><td>"
            for record in attendance_records:
                html += f"{record[0]}<br>"
            html += "</td><td>"
            for record in attendance_records:
                html += f"{record[1]}<br>"
            html += "</td></tr>"
        html += "</tbody></table>"
    return html
    

def take_attendance(request):
    # Call the ClassAttendance.py script
    try:
        subprocess.run(["python", "FacialRecognitionAttendance/ClassAttendance.py"])
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required(login_url='login')
@require_POST
def clear_attendance(request):
    try:
        attendance_file_path = os.path.join(settings.BASE_DIR, 'FacialRecognitionAttendance', 'Attendance.csv')
        # Clear the contents of the Attendance.csv file
        with open(attendance_file_path, 'w') as f:
            f.write("")

        return JsonResponse({'success': True})
    except Exception as e:
        logging.error(f"Error occurred while clearing attendance records: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})