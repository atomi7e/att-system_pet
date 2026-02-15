from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import path
from django.utils.html import format_html
from .models import Class, Group, Student, Attendance, Teacher

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'student_count', 'created_at']
    search_fields = ['name', 'code']
    
    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'Students'

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'classes_list', 'student_count']
    search_fields = ['code', 'name']
    # ВАЖНО: Это позволяет удобно добавлять предметы группе
    filter_horizontal = ['classes']
    
    def classes_list(self, obj):
        return ', '.join(c.code for c in obj.classes.all()) or '—'
    classes_list.short_description = 'Subjects'
    
    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'Students'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'student_id', 'group', 'has_account']
    search_fields = ['name', 'student_id']
    list_filter = ['group']
    
    def has_account(self, obj):
        return obj.user is not None
    has_account.boolean = True

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user_info', 'status_badge', 'department', 'assigned_summary', 'action_buttons']
    list_filter = ['status', 'department']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    actions = ['approve_teachers', 'reject_teachers']
    
    # ВАЖНО: Это возвращает "окошки" для выбора предметов и групп
    filter_horizontal = ['classes', 'groups']
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'phone', 'department')
        }),
        ('Assignments', {
            'fields': ('classes', 'groups'),
            'description': 'Select subjects and groups this teacher can manage.'
        }),
        ('Status', {
            'fields': ('status', 'rejection_reason')
        }),
    )
    
    def user_info(self, obj):
        return f"{obj.user.get_full_name()} ({obj.user.username})"
    
    def assigned_summary(self, obj):
        c_count = obj.classes.count()
        g_count = obj.groups.count()
        return f"{c_count} Subjects, {g_count} Groups"
    assigned_summary.short_description = 'Access'

    def status_badge(self, obj):
        colors = {'pending': 'orange', 'approved': 'green', 'rejected': 'red'}
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 8px; border-radius: 4px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )

    def action_buttons(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a class="button" href="{}">Approve</a>&nbsp;',
                f"/admin/attendance/teacher/{obj.id}/approve/"
            )
        return "—"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:teacher_id>/approve/', self.admin_site.admin_view(self.approve_teacher), name='teacher_approve'),
        ]
        return custom_urls + urls

    def approve_teacher(self, request, teacher_id):
        teacher = get_object_or_404(Teacher, id=teacher_id)
        teacher.status = 'approved'
        teacher.save()
        messages.success(request, f'Teacher {teacher.user.username} approved.')
        return redirect('admin:attendance_teacher_changelist')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['date', 'student', 'class_enrolled', 'status']
    list_filter = ['date', 'class_enrolled', 'status']