from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Базовые классы (на случай использования в других местах)
INPUT_CLASSES = "w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class StudentRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    student_id = forms.CharField(max_length=20)
    email = forms.EmailField(required=False)
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm password')
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username
    
    def clean_student_id(self):
        from .models import Student
        student_id = self.cleaned_data.get('student_id').strip()
        try:
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            raise forms.ValidationError('Student ID not found.')
        if student.user_id is not None:
            raise forms.ValidationError('Account already linked.')
        return student_id
    
    def clean(self):
        data = super().clean()
        if data.get('password1') != data.get('password2'):
            raise forms.ValidationError({'password2': 'Passwords do not match.'})
        return data
    
    def save(self):
        from .models import Student
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data.get('email') or '',
        )
        student = Student.objects.get(student_id=self.cleaned_data['student_id'])
        student.user = user
        student.save()
        return user

class TeacherRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=20, required=False)
    department = forms.CharField(max_length=100, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'department', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user