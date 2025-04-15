from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField()
    age = models.PositiveIntegerField()
    height = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 180.00
    weight = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 75.00
    chronic_illnesses = models.TextField()
    phone_number = models.CharField(max_length=20)
    has_aids = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"