from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Универсальный класс для всех полей ввода (ссылается на style.css)
INPUT_CLASSES = "form-input"

class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Enter username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Enter password'}))

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': INPUT_CLASSES}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': INPUT_CLASSES}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': INPUT_CLASSES}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class StudentRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Choose username'}))
    student_id = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g. 230521'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Optional'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': INPUT_CLASSES}), label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': INPUT_CLASSES}), label='Confirm password')
    
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
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': INPUT_CLASSES}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': INPUT_CLASSES}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': INPUT_CLASSES}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASSES}))
    department = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASSES}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'department', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': INPUT_CLASSES}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user