from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Q
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta
from .models import Class, Group, Student, Attendance, Teacher
from .forms import UserRegistrationForm, UserLoginForm, TeacherRegistrationForm, StudentRegistrationForm


def get_teacher(request):
    """Return approved Teacher for request.user or None."""
    if not request.user.is_authenticated:
        return None
    try:
        teacher = request.user.teacher_profile
        return teacher if teacher.is_approved() else None
    except Teacher.DoesNotExist:
        return None


def get_student(request):
    """Return Student linked to request.user or None."""
    if not request.user.is_authenticated:
        return None
    try:
        return request.user.student_profile
    except Student.DoesNotExist:
        return None


def register_choice(request):
    """Choose registration type: student or teacher."""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'attendance/register_choice.html')


def register(request):
    """Legacy general register — redirect to choice."""
    if request.user.is_authenticated:
        return redirect('home')
    return redirect('register_choice')


@ensure_csrf_cookie
def register_student(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! You can now log in and view your attendance.')
            return redirect('login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'attendance/register_student.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                # Redirect by role: student -> my attendance, teacher -> home (classes)
                try:
                    if user.student_profile:
                        return redirect('my_attendance')
                except Student.DoesNotExist:
                    pass
                if get_teacher(request):
                    return redirect('home')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'attendance/login.html', {'form': form})


def home(request):
    teacher = get_teacher(request)
    student = get_student(request)
    # Студент после входа видит свою посещаемость; на главную попадают только преподаватели/админы
    if student:
        return redirect('my_attendance')
    if teacher:
        classes = teacher.classes.all()
    else:
        classes = Class.objects.all()
    return render(request, 'attendance/home.html', {'classes': classes, 'is_teacher': teacher is not None})


def class_students(request, class_id):
    if get_student(request):
        return redirect('my_attendance')
    class_obj = get_object_or_404(Class, id=class_id)
    teacher = get_teacher(request)
    if teacher:
        if class_obj not in teacher.classes.all():
            messages.error(request, 'You do not have access to this subject.')
            return redirect('home')
        students = class_obj.students.filter(group__in=teacher.groups.all()).select_related('group')
    else:
        students = class_obj.students.select_related('group').all()
    return render(request, 'attendance/class_students.html', {
        'class_obj': class_obj,
        'students': students,
        'is_teacher': teacher is not None,
    })


def mark_attendance(request, class_id):
    if get_student(request):
        return redirect('my_attendance')
    class_obj = get_object_or_404(Class, id=class_id)
    teacher = get_teacher(request)
    group_id = request.GET.get('group_id')
    
    if teacher:
        if class_obj not in teacher.classes.all():
            messages.error(request, 'You do not have access to this subject.')
            return redirect('home')
        # Группы преподавателя, привязанные к этому предмету
        allowed_groups = teacher.groups.filter(classes=class_obj)
        if not group_id:
            # Показываем выбор группы
            return render(request, 'attendance/mark_attendance_select_group.html', {
                'class_obj': class_obj,
                'groups': allowed_groups,
                'is_teacher': True,
            })
        group = get_object_or_404(Group, id=group_id)
        if group not in teacher.groups.all() or class_obj not in group.classes.all():
            messages.error(request, 'You do not have access to this group for this subject.')
            return redirect('mark_attendance', class_id=class_id)
        students = group.students.select_related('group').all()
    else:
        students = class_obj.students.select_related('group').all()
    
    attendance_date = request.GET.get('date', date.today().isoformat())
    try:
        attendance_date = date.fromisoformat(attendance_date)
    except (ValueError, TypeError):
        attendance_date = date.today()
    
    existing_attendance = {}
    for student in students:
        attendance = Attendance.objects.filter(
            student=student,
            date=attendance_date,
            class_enrolled=class_obj
        ).first()
        if attendance:
            existing_attendance[student.id] = attendance.status
            student.current_status = attendance.status
        else:
            student.current_status = 'absent'
    
    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.id}', 'absent')
            attendance, created = Attendance.objects.update_or_create(
                student=student,
                date=attendance_date,
                class_enrolled=class_obj,
                defaults={'status': status}
            )
        return redirect('attendance_report_date', class_id=class_id, date_str=attendance_date.isoformat())
    
    selected_group = None
    if teacher and group_id:
        selected_group = group
    return render(request, 'attendance/mark_attendance.html', {
        'class_obj': class_obj,
        'students': students,
        'attendance_date': attendance_date,
        'existing_attendance': existing_attendance,
        'is_teacher': teacher is not None,
        'selected_group': selected_group,
        'group_id': group_id or '',
    })


def attendance_report(request, class_id, date_str=None):
    if get_student(request):
        return redirect('my_attendance')
    class_obj = get_object_or_404(Class, id=class_id)
    teacher = get_teacher(request)
    if teacher:
        if class_obj not in teacher.classes.all():
            messages.error(request, 'You do not have access to this subject.')
            return redirect('home')
        teacher_group_ids = list(teacher.groups.values_list('id', flat=True))
    
    if date_str:
        try:
            report_date = date.fromisoformat(date_str)
        except (ValueError, TypeError):
            report_date = date.today()
    else:
        date_param = request.GET.get('date', date.today().isoformat())
        try:
            report_date = date.fromisoformat(date_param)
        except (ValueError, TypeError):
            report_date = date.today()
    
    if teacher:
        attendances = Attendance.objects.filter(
            class_enrolled=class_obj,
            date=report_date,
            student__group_id__in=teacher_group_ids
        ).select_related('student', 'student__group')
        total_students = class_obj.students.filter(group_id__in=teacher_group_ids).count()
    else:
        attendances = Attendance.objects.filter(
            class_enrolled=class_obj,
            date=report_date
        ).select_related('student')
        total_students = class_obj.students.count()
    
    present_count = attendances.filter(status='present').count()
    absent_count = attendances.filter(status='absent').count()
    late_count = attendances.filter(status='late').count()
    
    return render(request, 'attendance/report.html', {
        'class_obj': class_obj,
        'attendances': attendances,
        'report_date': report_date,
        'total_students': total_students,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'is_teacher': teacher is not None,
    })


def my_attendance(request):
    """Личный кабинет студента: моя посещаемость (только для пользователей с привязанной записью студента)."""
    student = get_student(request)
    if not student:
        messages.info(request, 'This page is for students. Log in with your student account.')
        return redirect('login')
    attendances = Attendance.objects.filter(student=student).select_related('class_enrolled').order_by('-date')
    present_count = attendances.filter(status='present').count()
    absent_count = attendances.filter(status='absent').count()
    late_count = attendances.filter(status='late').count()
    total_records = attendances.count()
    attendance_percent = round(100 * present_count / total_records, 1) if total_records else 0
    # Статистика по каждому предмету отдельно
    class_ids = attendances.values_list('class_enrolled_id', flat=True).distinct()
    stats_by_subject = []
    for cid in class_ids:
        cls = Class.objects.get(id=cid)
        recs = Attendance.objects.filter(student=student, class_enrolled=cls)
        total = recs.count()
        p = recs.filter(status='present').count()
        a = recs.filter(status='absent').count()
        l = recs.filter(status='late').count()
        stats_by_subject.append({
            'class': cls,
            'present': p,
            'absent': a,
            'late': l,
            'total': total,
            'percent': round(100 * p / total, 1) if total else 0,
        })
    first_class = student.group.classes.first()
    return render(request, 'attendance/my_attendance.html', {
        'student': student,
        'first_class': first_class,
        'attendances': attendances,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'total_records': total_records,
        'attendance_percent': attendance_percent,
        'stats_by_subject': stats_by_subject,
    })


def student_detail(request, student_id):
    student = get_object_or_404(Student.objects.select_related('group').prefetch_related('group__classes'), id=student_id)
    logged_student = get_student(request)
    teacher = get_teacher(request)
    # Студент может смотреть только свою карточку
    if logged_student:
        if student.id != logged_student.id:
            messages.error(request, 'You can only view your own attendance.')
            return redirect('my_attendance')
    elif teacher:
        if student.group not in teacher.groups.all():
            messages.error(request, 'You do not have access to this student.')
            return redirect('home')
    # Неавторизованный или админ — можно смотреть любого
    attendances = Attendance.objects.filter(student=student).select_related('class_enrolled').order_by('-date')
    
    present_count = attendances.filter(status='present').count()
    absent_count = attendances.filter(status='absent').count()
    late_count = attendances.filter(status='late').count()
    
    first_class = student.group.classes.first()
    is_own = bool(logged_student and student.id == logged_student.id)
    return render(request, 'attendance/student_detail.html', {
        'student': student,
        'first_class': first_class,
        'attendances': attendances,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'is_own': is_own,
    })


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def register_teacher(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create Teacher profile with pending status
            Teacher.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone', ''),
                department=form.cleaned_data.get('department', ''),
                status='pending'
            )
            username = form.cleaned_data.get('username')
            messages.success(
                request, 
                f'Teacher registration submitted for {username}! Your request is pending admin approval. '
                'You will be notified once your registration is reviewed.'
            )
            return redirect('login')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'attendance/register_teacher.html', {'form': form})
