from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    notification_preference = models.CharField(
        max_length=10,
        choices=[('email', 'Email'), ('sms', 'SMS'), ('both', 'Both')],
        default='email'
    )
    
    def __str__(self):
        return self.username
