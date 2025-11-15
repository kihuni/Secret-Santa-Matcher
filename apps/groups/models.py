from django.db import models
from django.contrib.auth import get_user_model
import uuid
import secrets

User = get_user_model()

class Group(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_groups')
    invite_code = models.CharField(max_length=12, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    matching_done = models.BooleanField(default=False)
    reveal_mode = models.BooleanField(default=False)
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = secrets.token_urlsafe(8)[:12].upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Member(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    wishlist = models.TextField(blank=True, help_text="Enter 3 gift ideas, one per line")
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('group', 'user')
    
    def __str__(self):
        return f"{self.user.username} in {self.group.name}"

class Match(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='matches')
    giver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='giving_to')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiving_from')
    notification_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('group', 'giver')
    
    def __str__(self):
        return f"{self.giver.username} → {self.receiver.username}"
