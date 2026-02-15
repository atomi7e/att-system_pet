from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Class(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Classes"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def students(self):
        """Students in this class (via groups)."""
        return Student.objects.filter(group__classes=self)


class Group(models.Model):
    """Учебная группа (например cs-2301). Может быть привязана к нескольким классам/курсам."""
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100, blank=True)
    classes = models.ManyToManyField(Class, related_name='groups', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['code']
        verbose_name_plural = "Groups"
    
    def __str__(self):
        return self.code or self.name or str(self.id)


class Student(models.Model):
    name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='students')
    # Связь с аккаунтом пользователя (студент регистрируется и привязывает аккаунт к своей записи)
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='student_profile'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.student_id})"
    
    def has_account(self):
        return self.user_id is not None


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    notes = models.TextField(blank=True)
    marked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', 'student']
        # Отдельный лист посещаемости на каждый предмет: студент + дата + предмет = одна запись
        unique_together = [['student', 'date', 'class_enrolled']]
    
    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.class_enrolled.code} - {self.status}"


class Teacher(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    # Предметы и группы, которые ведёт преподаватель (только по ним может ставить посещаемость)
    classes = models.ManyToManyField(Class, related_name='teachers', blank=True, verbose_name='Subjects')
    groups = models.ManyToManyField(Group, related_name='teachers', blank=True, verbose_name='Groups')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_teachers')
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection (if rejected)")
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name_plural = "Teachers"
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username}) - {self.get_status_display()}"
    
    def is_approved(self):
        return self.status == 'approved'
    
    def is_pending(self):
        return self.status == 'pending'
