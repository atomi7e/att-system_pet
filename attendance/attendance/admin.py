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
    search_fields = ['name', 'code', 'description']
    list_filter = ['created_at']
    
    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'Students'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'classes_list', 'student_count', 'created_at']
    search_fields = ['code', 'name']
    list_filter = ['classes']
    filter_horizontal = ['classes']
    
    def classes_list(self, obj):
        return ', '.join(c.code for c in obj.classes.all()) or '—'
    classes_list.short_description = 'Classes'
    
    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'Students'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'student_id', 'group', 'email', 'has_account', 'created_at']
    search_fields = ['name', 'student_id', 'email']
    list_filter = ['group', 'group__classes']
    list_select_related = ['group']
    
    def has_account(self, obj):
        return obj.has_account()
    has_account.boolean = True
    has_account.short_description = 'Has account'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_enrolled', 'date', 'status', 'marked_at']
    search_fields = ['student__name', 'student__student_id', 'class_enrolled__name']
    list_filter = ['status', 'date', 'class_enrolled']
    date_hierarchy = 'date'
    list_select_related = ['student', 'class_enrolled']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user_info', 'status_badge', 'department', 'phone', 'submitted_at', 'reviewed_info', 'action_buttons']
    list_filter = ['status', 'submitted_at', 'department']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email', 'department']
    readonly_fields = ['submitted_at', 'reviewed_at', 'reviewed_by']
    actions = ['approve_teachers', 'reject_teachers']
    
    filter_horizontal = ['classes', 'groups']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone', 'department')
        }),
        ('Assigned subjects and groups', {
            'fields': ('classes', 'groups'),
            'description': 'Teacher can only mark attendance for these subjects and groups.'
        }),
        ('Registration Status', {
            'fields': ('status', 'submitted_at', 'reviewed_at', 'reviewed_by', 'rejection_reason')
        }),
    )
    
    def user_info(self, obj):
        return f"{obj.user.get_full_name()} ({obj.user.username})"
    user_info.short_description = 'Teacher'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#f39c12',
            'approved': '#27ae60',
            'rejected': '#e74c3c'
        }
        color = colors.get(obj.status, '#7f8c8d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def reviewed_info(self, obj):
        if obj.reviewed_at:
            reviewer = obj.reviewed_by.username if obj.reviewed_by else 'System'
            return f"{obj.reviewed_at.strftime('%Y-%m-%d %H:%M')} by {reviewer}"
        return "—"
    reviewed_info.short_description = 'Reviewed'
    
    def action_buttons(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a class="button" href="/admin/attendance/teacher/{}/approve/">Approve</a>&nbsp;'
                '<a class="button" href="/admin/attendance/teacher/{}/reject/">Reject</a>',
                obj.id, obj.id
            )
        return "—"
    action_buttons.short_description = 'Actions'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:teacher_id>/approve/', self.admin_site.admin_view(self.approve_teacher), name='teacher_approve'),
            path('<int:teacher_id>/reject/', self.admin_site.admin_view(self.reject_teacher), name='teacher_reject'),
        ]
        return custom_urls + urls
    
    def approve_teacher(self, request, teacher_id):
        teacher = get_object_or_404(Teacher, id=teacher_id)
        if teacher.status == 'pending':
            teacher.status = 'approved'
            teacher.reviewed_at = timezone.now()
            teacher.reviewed_by = request.user
            teacher.save()
            messages.success(request, f'Teacher {teacher.user.get_full_name()} has been approved.')
        else:
            messages.warning(request, 'This teacher registration has already been processed.')
        return redirect('admin:attendance_teacher_changelist')
    
    def reject_teacher(self, request, teacher_id):
        teacher = get_object_or_404(Teacher, id=teacher_id)
        if teacher.status == 'pending':
            teacher.status = 'rejected'
            teacher.reviewed_at = timezone.now()
            teacher.reviewed_by = request.user
            teacher.save()
            messages.success(request, f'Teacher {teacher.user.get_full_name()} has been rejected.')
        else:
            messages.warning(request, 'This teacher registration has already been processed.')
        return redirect('admin:attendance_teacher_changelist')
    
