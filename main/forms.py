from django import forms
from django.contrib.auth.models import User
from .models import Patient, Appointment, Doctor
import datetime


class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(required=True, label="Username")
    email = forms.EmailField(required=True, label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password", required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password", required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            self.add_error('confirm_password', "Passwords do not match")


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name',
            'last_name',
            'address',
            'age',
            'height',
            'weight',
            'chronic_illnesses',
            'has_aids'
        ]


class AppointmentForm(forms.ModelForm):
    appointment_type = forms.ChoiceField(
        choices=Appointment.TYPE_CHOICES,
        widget=forms.RadioSelect,
        label="Is it an emergency?"
    )

    appointment_date = forms.DateField(
        widget=forms.SelectDateWidget,
        label="Preferred Date",
    )

    class Meta:
        model = Appointment
        fields = ['appointment_type', 'appointment_date', 'appointment_time', 'doctor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = datetime.date.today()
        self.fields['appointment_date'].widget.years = [today.year]
        self.fields['appointment_date'].widget.attrs['min'] = today + datetime.timedelta(days=1)
        self.fields['appointment_date'].widget.attrs['max'] = today + datetime.timedelta(days=7)

        self.fields['appointment_time'].widget = forms.Select(choices=[
            (f"{h:02d}:00", f"{h:02d}:00") for h in range(9, 21)
        ])

        self.fields['doctor'].queryset = Doctor.objects.all()