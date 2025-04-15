from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField()
    age = models.PositiveIntegerField()
    height = models.DecimalField(max_digits=5, decimal_places=2)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    chronic_illnesses = models.TextField()
    phone_number = models.CharField(max_length=20)
    sms_gateway = models.CharField(max_length=100, default="default.com")  # 💬 email-to-text
    has_aids = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Doctor(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    TYPE_CHOICES = [
        ('AE', 'Emergency (A&E)'),
        ('GC', 'General Check-Up'),
    ]
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Checked-In', 'Checked-In'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
        ('Rescheduled', 'Rescheduled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    appointment_type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    is_emergency = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.get_appointment_type_display()} on {self.appointment_date} at {self.appointment_time}"