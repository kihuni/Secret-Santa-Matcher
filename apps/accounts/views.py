from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, ProfileUpdateForm

def signup(request):
    """Register a new user"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name or user.username}! Your account has been created.')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def logout_view(request):
    """Log out the current user"""
    logout(request)
    messages.info(request, 'You have been logged out. See you next time! 🎅')
    return redirect('home')

@login_required
def profile(request):
    """View and edit user profile"""
    groups = request.user.memberships.select_related('group').all()
    hosted = request.user.hosted_groups.all()
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'groups': groups,
        'hosted_groups': hosted,
        'total_groups': groups.count(),
    }
    return render(request, 'accounts/profile.html', context)