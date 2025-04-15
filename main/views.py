from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, PatientForm, AppointmentForm
from .models import Appointment, Doctor
import datetime

def home(request):
    return render(request, 'index.html')

@login_required
def book(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment_type = form.cleaned_data['appointment_type']

            if appointment_type == 'AE':
                Appointment.objects.create(
                    user=request.user,
                    appointment_type='AE',
                    is_emergency=True,
                    appointment_date=datetime.date.today(),
                    appointment_time=datetime.datetime.now().time(),
                    status='Scheduled'
                )
                messages.success(request, 'Emergency registered. Go to A&E department immediately!')
                return redirect('home')

            date = form.cleaned_data['appointment_date']
            time = form.cleaned_data['appointment_time']
            doctor = form.cleaned_data['doctor']

            exists = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=date,
                appointment_time=time,
                status='Scheduled'
            ).exists()

            if exists:
                messages.error(request, f"{doctor.name} is already booked at that time.")
            else:
                Appointment.objects.create(
                    user=request.user,
                    appointment_type='GC',
                    is_emergency=False,
                    appointment_date=date,
                    appointment_time=time,
                    doctor=doctor,
                    status='Scheduled'
                )
                messages.success(request, 'Your appointment was booked successfully!')
                return redirect('home')
    else:
        form = AppointmentForm()

    return render(request, 'book.html', {'form': form})

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

@login_required
def manage(request):
    appointments = Appointment.objects.filter(user=request.user).order_by('-appointment_date', '-appointment_time')

    if request.method == 'POST':
        appointment_id = request.POST.get('cancel_id')
        if appointment_id:
            try:
                appointment = Appointment.objects.get(id=appointment_id, user=request.user)
                if appointment.status == 'Scheduled':
                    appointment.status = 'Cancelled'
                    appointment.save()
                    messages.success(request, 'Appointment cancelled successfully.')
                else:
                    messages.warning(request, 'Only scheduled appointments can be cancelled.')
            except Appointment.DoesNotExist:
                messages.error(request, 'Appointment not found.')

        return redirect('manage')

    return render(request, 'manage.html', {'appointments': appointments})

@login_required
def reschedule(request, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id, user=request.user)
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found.")
        return redirect('manage')

    if appointment.status != 'Scheduled':
        messages.warning(request, "Only scheduled appointments can be rescheduled.")
        return redirect('manage')

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['appointment_date']
            time = form.cleaned_data['appointment_time']
            doctor = form.cleaned_data['doctor']

            exists = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=date,
                appointment_time=time,
                status='Scheduled'
            ).exclude(id=appointment.id).exists()

            if exists:
                messages.error(request, f"{doctor.name} is already booked at that time.")
            else:
                appointment.appointment_date = date
                appointment.appointment_time = time
                appointment.doctor = doctor
                appointment.status = 'Rescheduled'
                appointment.save()
                messages.success(request, 'Appointment rescheduled successfully.')
                return redirect('manage')
    else:
        form = AppointmentForm(initial={
            'appointment_type': appointment.appointment_type,
            'appointment_date': appointment.appointment_date,
            'appointment_time': appointment.appointment_time.strftime("%H:%M"),
            'doctor': appointment.doctor,
        })

    return render(request, 'reschedule.html', {'form': form, 'appointment': appointment})