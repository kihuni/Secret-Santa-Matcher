from django import forms
from .models import Group, Member

class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'budget_limit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Family Christmas 2025'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
            'budget_limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Optional (e.g., 50)'}),
        }

class JoinGroupForm(forms.Form):
    invite_code = forms.CharField(
        max_length=12,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter invite code',
            'style': 'text-transform: uppercase;'
        })
    )

class WishlistForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['wishlist']
        widgets = {
            'wishlist': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': '1. Cozy blanket\n2. Coffee mug set\n3. Gift card to favorite store'
            })
        }
        labels = {
            'wishlist': 'Your Gift Wishlist (3 ideas)'
        }