from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=50)
    year = models.IntegerField()
    section = models.CharField(max_length=10)

    def __str__(self):
        return self.roll_number

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username

class Circular(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='circulars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField()

    def __str__(self):
        return self.title

class Classroom(models.Model):
    room_number = models.CharField(max_length=20)
    capacity = models.IntegerField()

    def __str__(self):
        return self.room_number

class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    marks = models.IntegerField()

    def __str__(self):
        return f"{self.student.roll_number} - {self.subject}"

class SeatingArrangement(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    seat_number = models.IntegerField()

    def __str__(self):
        return f"{self.student.roll_number} - {self.classroom.room_number}"


