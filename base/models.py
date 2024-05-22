from django.db import models
from django.contrib.auth.models import User
    
class Course(models.Model):
    course_name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.course_name  

class Student(models.Model):
    first_name = models.CharField(max_length=50, default="")
    last_name = models.CharField(max_length=50, default="")
    face_image = models.ImageField(upload_to='student_faces')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Attendance(models.Model):
    student_name = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student_name} - {self.date} - {self.time}"
