from .models import Teacher, Student


def attendance_roles(request):
    """Add is_student and is_teacher to template context."""
    is_teacher = False
    is_student = False
    if request.user.is_authenticated:
        try:
            if request.user.teacher_profile.is_approved():
                is_teacher = True
        except (Teacher.DoesNotExist, AttributeError):
            pass
        try:
            request.user.student_profile
            is_student = True
        except Student.DoesNotExist:
            pass
    return {'is_teacher': is_teacher, 'is_student': is_student}
