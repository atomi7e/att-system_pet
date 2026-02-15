from rest_framework import serializers
from .models import Class, Group, Student, Attendance


class ClassSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = ['id', 'name', 'code', 'description', 'student_count', 'created_at']
    
    def get_student_count(self, obj):
        return obj.students.count()


class GroupSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ['id', 'code', 'name', 'classes', 'student_count', 'created_at']
    
    def get_student_count(self, obj):
        return obj.students.count()


class StudentSerializer(serializers.ModelSerializer):
    group_code = serializers.CharField(source='group.code', read_only=True)
    
    class Meta:
        model = Student
        fields = ['id', 'name', 'student_id', 'email', 'group', 'group_code', 'created_at']


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    class_name = serializers.CharField(source='class_enrolled.name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = ['id', 'student', 'student_name', 'student_id', 'class_enrolled', 'class_name', 
                  'date', 'status', 'notes', 'marked_at']


