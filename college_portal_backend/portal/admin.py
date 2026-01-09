from django.contrib import admin
from .models import Student, Faculty, Circular, Classroom, Marks, SeatingArrangement

admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(Circular)
admin.site.register(Classroom)
admin.site.register(Marks)
admin.site.register(SeatingArrangement)
