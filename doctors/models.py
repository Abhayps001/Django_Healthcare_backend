from django.db import models


class Doctor(models.Model):
    name = models.CharField(max_length=150)
    specialization = models.CharField(max_length=120)
    email = models.EmailField()
    phone_number = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.specialization})"
