from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from .forms import UserRegisterForm, PatientForm

def home(request):
    return render(request, 'index.html')

def book(request):
    return render(request, 'book.html')

def manage(request):
    return render(request, 'manage.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        patient_form = PatientForm(request.POST)

        if user_form.is_valid() and patient_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            patient = patient_form.save(commit=False)
            patient.user = user
            patient.save()

            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        user_form = UserRegisterForm()
        patient_form = PatientForm()

    return render(request, 'register.html', {
        'user_form': user_form,
        'patient_form': patient_form,
    })