from django.contrib import admin
from .models import *

admin.site.register(Department)
admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(Subject)
admin.site.register(Exam)
admin.site.register(Classroom)
admin.site.register(SeatingAllocation)
admin.site.register(Marks)
admin.site.register(Circular)

