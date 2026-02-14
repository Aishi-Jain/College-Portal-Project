from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Student, Faculty, Marks, Circular, SeatingArrangement

def home(request):
    return render(request, 'home.html')

def generate_seating_allocation():
    """
    Pure seating allocation logic.
    NO request, NO decorators.
    """
    SeatingArrangement.objects.all().delete()

    students = Student.objects.order_by('roll_number')
    classrooms = Classroom.objects.all().order_by('room_number')

    seat_counter = 0
    student_index = 0

    for classroom in classrooms:
        for seat in range(1, classroom.capacity + 1):
            if student_index >= students.count():
                return

            SeatingArrangement.objects.create(
                classroom=classroom,
                student=students[student_index],
                seat_number=seat
            )

            student_index += 1


# LOGIN VIEW
def login_view(request):
    role = request.GET.get('role', 'user')

    title_map = {
        'admin': 'Admin Login',
        'faculty': 'Faculty Login',
        'student': 'Student Login',
    }

    title = title_map.get(role, 'Login')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if user.is_superuser:
                return redirect('admin_dashboard')

            elif hasattr(user, 'faculty'):
                return redirect('faculty_dashboard')

            elif hasattr(user, 'student'):
                return redirect('student_dashboard')

        else:
            return render(request, 'login.html', {
                'error': 'Invalid credentials',
                'role': role
            })

    return render(request, 'login.html', {
        'title': title,
        'role': role
    })

# DASHBOARD REDIRECT (ROLE CHECK)
@login_required
def dashboard_redirect(request):
    user = request.user

    if user.is_superuser:
        return redirect('admin_dashboard')

    if hasattr(user, 'faculty'):
        return redirect('faculty_dashboard')

    if hasattr(user, 'student'):
        return redirect('student_dashboard')

    return redirect('login')


# ADMIN DASHBOARD
@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


# FACULTY DASHBOARD
@login_required
def faculty_dashboard(request):
    return render(request, 'faculty_dashboard.html')


# STUDENT DASHBOARD
@login_required
def student_dashboard(request):
    return render(request, 'student_dashboard.html')


# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('login')

import csv
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import Student

@login_required
def upload_students(request):
    if not request.user.is_superuser:
        return redirect('login')

    message = None

    if request.method == 'POST':

        # -------------------------------
        # CASE 1: CSV UPLOAD
        # -------------------------------
        if 'file' in request.FILES:
            csv_file = request.FILES['file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            created = 0
            skipped = 0

            for row in reader:
                username = row['username']

                if User.objects.filter(username=username).exists():
                    skipped += 1
                    continue

                user = User.objects.create_user(
                    username=username,
                    password=row['password']
                )

                Student.objects.create(
                    user=user,
                    roll_number=row['roll_number'],
                    department=row['department'],
                    year=row['year'],
                    section=row['section']
                )

                created += 1

            message = f"Upload complete. Created: {created}, Skipped: {skipped}"

        # -------------------------------
        # CASE 2: GENERATE SEATING
        # -------------------------------
        elif 'generate_seating' in request.POST:
            generate_seating_allocation()
            message = "Seating allocation generated successfully."

    return render(request, 'upload_students.html', {'message': message})


@login_required
def trigger_seating(request):
    if not request.user.is_superuser:
        return redirect('login')

    return HttpResponse("Seating algorithm triggered (logic will be added in Phase 4)")

''' import re

def roll_sort_key(roll):
    """
    Converts roll number into sortable components.
    Example:
    22Q91A6601 → (6601, '')
    22Q91A66A3 → (6699, 'A3')
    """
    tail = roll[-4:]

    if tail.isdigit():
        return (int(tail), '')
    else:
        number = int(tail[:2])
        letter_part = tail[2:]
        return (number + 100, letter_part) '''

import re

def roll_sort_key(roll):
    """
    Ensures order:
    6601–6699 first
    then A0–J0
    """

    suffix = roll[-4:]  # last 4 characters

    # Case 1: purely numeric (6601–6699)
    if suffix.isdigit():
        return (0, int(suffix))

    # Case 2: alphanumeric (A0–J0)
    letter = suffix[2]      # A, B, C...
    digit = int(suffix[3]) # 0–9

    return (1, ord(letter), digit)


from .models import Student, Classroom, SeatingArrangement
from django.http import HttpResponse
from django.db import transaction

@login_required
def allocate_seating(request):
    if not request.user.is_superuser:
        return redirect('login')

    students = list(Student.objects.all())
    classrooms = Classroom.objects.all().order_by('room_number')

    # Sort students using custom roll logic
    students.sort(key=lambda s: roll_sort_key(s.roll_number))

    SeatingArrangement.objects.all().delete()  # clear old allocations

    student_index = 0

    with transaction.atomic():
        for classroom in classrooms:
            for seat in range(1, classroom.capacity + 1):
                if student_index >= len(students):
                    break

                SeatingArrangement.objects.create(
                    student=students[student_index],
                    classroom=classroom,
                    seat_number=seat
                )

                student_index += 1

    return HttpResponse("Seating Allocation Completed Successfully")

from .models import SeatingArrangement

@login_required
def admin_seating_view(request):
    if not request.user.is_superuser:
        return redirect('login')

    allocations = SeatingArrangement.objects.select_related(
        'student', 'classroom'
    ).order_by('classroom__room_number', 'seat_number')

    return render(request, 'admin_seating.html', {
        'allocations': allocations
    })

@login_required
def admin_circulars(request):
    # 🔐 Only admins allowed
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        expiry_date = request.POST.get('expiry_date')

        Circular.objects.create(
            title=title,
            content=content,
            expiry_date=expiry_date,
            created_by=request.user
        )

        # 🔁 Stay on same page after publish
        return redirect('admin_circulars')

    circulars = Circular.objects.all().order_by('-created_at')

    return render(
        request,
        'admin_circulars.html',
        {'circulars': circulars}
    )

@login_required
def admin_add_circular(request):
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        expiry_date = request.POST.get('expiry_date')

        Circular.objects.create(
            title=title,
            content=content,
            expiry_date=expiry_date,
            created_by=request.user
        )

        return redirect('admin_circulars')

    return render(request, 'admin_add_circulars.html')

@login_required
def faculty_seating_view(request):
    if not hasattr(request.user, 'faculty'):
        return redirect('login')

    allocations = SeatingArrangement.objects.select_related(
        'student', 'classroom'
    ).order_by('classroom__room_number', 'seat_number')

    return render(
        request,
        'faculty_seating.html',
        {'allocations': allocations}
    )

from django.utils import timezone

from .models import Marks, Student

@login_required
def faculty_add_marks(request):
    if not hasattr(request.user, 'faculty'):
        return redirect('login')

    message = ""

    if request.method == 'POST':
        roll = request.POST['roll']
        subject = request.POST['subject']
        marks_value = request.POST['marks']

        try:
            student = Student.objects.get(roll_number=roll)

            Marks.objects.update_or_create(
                student=student,
                subject=subject,
                defaults={'marks': marks_value}
            )

            message = "Marks saved successfully"

        except Student.DoesNotExist:
            message = "Student with this roll number does not exist"

    return render(
        request,
        'faculty_add_marks.html',
        {'message': message}
    )

@login_required
def faculty_circulars(request):
    if not hasattr(request.user, 'faculty'):
        return redirect('login')

    circulars = Circular.objects.all().order_by('-created_at')
    return render(
        request,
        'faculty_circulars.html',
        {'circulars': circulars}
    )

@login_required
def faculty_add_circular(request):
    if not hasattr(request.user, 'faculty'):
        return redirect('login')

    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        expiry_date = request.POST['expiry_date']
        file = request.FILES.get('file')

        Circular.objects.create(
            title=title,
            description=description,
            expiry_date=expiry_date,
            file=file
        )

        return redirect('/faculty/circulars/')

    return render(request, 'faculty_add_circular.html')


@login_required
def student_seating_view(request):
    if not hasattr(request.user, 'student'):
        return redirect('login')

    allocation = SeatingArrangement.objects.filter(
        student=request.user.student
    ).first()

    return render(
        request,
        'student_seating.html',
        {'allocation': allocation}
    )

@login_required
def student_marks_view(request):
    if not hasattr(request.user, 'student'):
        return redirect('login')

    marks = Marks.objects.filter(
        student=request.user.student
    )

    return render(
        request,
        'student_marks.html',
        {'marks': marks}
    )

@login_required
def student_circulars(request):
    if not hasattr(request.user, 'student'):
        return redirect('login')

    circulars = Circular.objects.all().order_by('-id')
    return render(request, 'student_circulars.html', {'circulars': circulars})
