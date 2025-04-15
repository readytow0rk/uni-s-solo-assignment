from django import forms
from django.contrib.auth.models import User
from .models import Patient

class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(required=True, label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password", required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password", required=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            self.add_error('confirm_password', "Passwords do not match")


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'address', 'age', 'height', 'weight', 'chronic_illnesses', 'phone_number', 'has_aids']