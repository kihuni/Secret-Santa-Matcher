from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, unique=True)  # unique join code
    created_at = models.DateTimeField(auto_now_add=True)
    is_matched = models.BooleanField(default=False)

class Member(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    wishlist = models.TextField(blank=True)
    matched_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

