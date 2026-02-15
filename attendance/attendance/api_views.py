from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import date
from .models import Class, Student, Attendance
from .serializers import ClassSerializer, StudentSerializer, AttendanceSerializer


@api_view(['GET'])
def api_attendance_list(request):
    attendances = Attendance.objects.select_related('student', 'class_enrolled').all()
    
    class_id = request.GET.get('class_id')
    if class_id:
        attendances = attendances.filter(class_enrolled_id=class_id)
    
    date_param = request.GET.get('date')
    if date_param:
        try:
            filter_date = date.fromisoformat(date_param)
            attendances = attendances.filter(date=filter_date)
        except (ValueError, TypeError):
            pass
    
    student_id = request.GET.get('student_id')
    if student_id:
        attendances = attendances.filter(student_id=student_id)
    
    serializer = AttendanceSerializer(attendances, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def api_mark_attendance(request):
    student_id = request.data.get('student_id')
    class_id = request.data.get('class_id')
    date_str = request.data.get('date')
    status_val = request.data.get('status', 'absent')
    
    if not all([student_id, class_id, date_str]):
        return Response(
            {'error': 'Missing required fields: student_id, class_id, date'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        student = get_object_or_404(Student, id=student_id)
        class_obj = get_object_or_404(Class, id=class_id)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        attendance_date = date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if status_val not in ['present', 'absent', 'late']:
        return Response(
            {'error': 'Invalid status. Must be: present, absent, or late'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    attendance, created = Attendance.objects.update_or_create(
        student=student,
        date=attendance_date,
        class_enrolled=class_obj,
        defaults={
            'status': status_val,
            'notes': request.data.get('notes', '')
        }
    )
    
    serializer = AttendanceSerializer(attendance)
    return Response(
        serializer.data,
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
    )


@api_view(['GET', 'PUT', 'DELETE'])
def api_attendance_detail(request, attendance_id):
    try:
        attendance = Attendance.objects.select_related('student', 'class_enrolled').get(id=attendance_id)
    except Attendance.DoesNotExist:
        return Response(
            {'error': 'Attendance record not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        status_val = request.data.get('status', attendance.status)
        notes = request.data.get('notes', attendance.notes)
        
        if status_val not in ['present', 'absent', 'late']:
            return Response(
                {'error': 'Invalid status. Must be: present, absent, or late'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        date_str = request.data.get('date')
        if date_str:
            try:
                attendance_date = date.fromisoformat(date_str)
                attendance.date = attendance_date
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        attendance.status = status_val
        attendance.notes = notes
        attendance.save()
        
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        attendance.delete()
        return Response(
            {'message': 'Attendance record deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )

