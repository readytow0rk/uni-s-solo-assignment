from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .forms import UserRegisterForm, PatientForm, AppointmentForm
from .models import Appointment, Doctor, Patient, CheckIn
import datetime
from django.shortcuts import get_object_or_404
from .models import CheckIn

@login_required
def check_in(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)

    if appointment.status in ['Scheduled', 'Rescheduled']:
        CheckIn.objects.get_or_create(appointment=appointment, defaults={'checked_in_at': timezone.now()})
        appointment.status = 'Checked-In'
        appointment.save()
        messages.success(request, '✅ You are now checked in.')
    else:
        messages.error(request, '❌ Cannot check in for this appointment.')

    return redirect('manage')

def home(request):
    return render(request, 'index.html')

@login_required
def book(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment_type = form.cleaned_data['appointment_type']
            user_email = request.user.email

            if appointment_type == 'AE':
                Appointment.objects.create(
                    user=request.user,
                    appointment_type='AE',
                    is_emergency=True,
                    appointment_date=datetime.date.today(),
                    appointment_time=datetime.datetime.now().time(),
                    status='Scheduled'
                )

                send_mail(
                    subject='🚨 Emergency Appointment Confirmation',
                    message='You are registered for an emergency appointment. Please go to A&E immediately.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user_email],
                    fail_silently=False,
                )

                messages.success(request, '🚨 Emergency registered. Go to A&E immediately.')
                return render(request, 'book.html', {'form': AppointmentForm()})

            date = form.cleaned_data['appointment_date']
            time = form.cleaned_data['appointment_time']
            doctor = form.cleaned_data['doctor']

            exists = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=date,
                appointment_time=time,
                status__in=['Scheduled', 'Rescheduled']
            ).exists()

            if exists:
                messages.error(request, f"{doctor.name} is already booked at {time}.")
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

                send_mail(
                    subject='✅ Appointment Booked',
                    message=f"Hi {request.user.username}, your appointment with Dr. {doctor.name} has been booked for {date} at {time}.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user_email],
                    fail_silently=False,
                )

                messages.success(request, '✅ Appointment booked successfully!')
                return render(request, 'book.html', {'form': AppointmentForm()})
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
            user.email = user_form.cleaned_data['email']
            user.save()

            patient = patient_form.save(commit=False)
            patient.user = user
            patient.save()

            send_mail(
                subject='👋 Welcome to the Appointment System',
                message=f"Hi {user.username}, your account has been created successfully. You can now book appointments.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.success(request, '✅ Account created successfully! You can now log in.')
            return redirect('login')
    else:
        user_form = UserRegisterForm()
        patient_form = PatientForm()

    return render(request, 'register.html', {
        'user_form': user_form,
        'patient_form': patient_form,
    })

from datetime import datetime, timedelta

@login_required
def manage(request):
    appointments = Appointment.objects.filter(user=request.user).order_by('-appointment_date', '-appointment_time')
    now = datetime.now()

    if request.method == 'POST':
        appointment_id = request.POST.get('cancel_id')
        if appointment_id:
            try:
                appointment = Appointment.objects.get(id=appointment_id, user=request.user)
                if appointment.status in ['Scheduled', 'Rescheduled']:
                    send_mail(
                        subject='❌ Appointment Cancelled',
                        message=f"Hi {request.user.username}, your appointment with Dr. {appointment.doctor.name if appointment.doctor else 'our team'} on {appointment.appointment_date} at {appointment.appointment_time} has been cancelled.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[request.user.email],
                        fail_silently=False,
                    )
                    appointment.delete()
                    messages.success(request, 'Appointment cancelled and deleted.')
                else:
                    messages.warning(request, 'Only scheduled or rescheduled appointments can be deleted.')
            except Appointment.DoesNotExist:
                messages.error(request, 'Appointment not found.')

        return redirect('manage')

    return render(request, 'manage.html', {'appointments': appointments, 'now': now})

@login_required
def reschedule(request, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id, user=request.user)
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found.")
        return redirect('manage')

    if appointment.status not in ['Scheduled', 'Rescheduled']:
        messages.warning(request, "Only scheduled appointments can be rescheduled.")
        return redirect('manage')

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            new_date = form.cleaned_data['appointment_date']
            new_time = form.cleaned_data['appointment_time']
            new_doctor = form.cleaned_data['doctor']

            conflict = Appointment.objects.filter(
                doctor=new_doctor,
                appointment_date=new_date,
                appointment_time=new_time,
                status__in=['Scheduled', 'Rescheduled']
            ).exclude(id=appointment.id).exists()

            if conflict:
                messages.error(request, f"{new_doctor.name} is already booked at {new_time}.")
            else:
                appointment.appointment_date = new_date
                appointment.appointment_time = new_time
                appointment.doctor = new_doctor
                appointment.status = 'Rescheduled'
                appointment.save()

                send_mail(
                    subject='🗕️ Appointment Rescheduled',
                    message=(
                        f"Hi {request.user.username},\n\n"
                        f"Your appointment has been successfully rescheduled with Dr. {new_doctor.name} "
                        f"to {new_date} at {new_time}.\n\n"
                        f"- Hospital System"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )

                messages.success(request, "✅ Appointment rescheduled successfully.")
                return redirect('manage')
    else:
        initial_time = appointment.appointment_time.strftime("%H:%M")

        form = AppointmentForm(initial={
            'appointment_type': appointment.appointment_type,
            'appointment_date': appointment.appointment_date,
            'appointment_time': initial_time,
            'doctor': appointment.doctor,
        })

    return render(request, 'reschedule.html', {'form': form, 'appointment': appointment})

@login_required
def check_in(request, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id, user=request.user)

        if appointment.status in ['Scheduled', 'Rescheduled']:
            appointment.status = 'Checked-In'
            appointment.save()

            # Optional: log it to admin via email or log system

            messages.success(request, '✅ You have checked in for your appointment.')
        else:
            messages.warning(request, 'Cannot check in. Appointment is not active.')
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found.")

    return redirect('manage')