from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .models import Group, Member, Match
from .forms import GroupCreateForm, JoinGroupForm, WishlistForm
from .matcher import SecretSantaMatcher
from .tasks import send_all_match_notifications

@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.host = request.user
            group.save()
            
            # Auto-join creator as member
            Member.objects.create(group=group, user=request.user)
            
            messages.success(request, f'Group "{group.name}" created! Share invite code: {group.invite_code}')
            return redirect('group_detail', group_id=group.id)
    else:
        form = GroupCreateForm()
    
    return render(request, 'groups/create.html', {'form': form})

@login_required
def join_group(request):
    if request.method == 'POST':
        form = JoinGroupForm(request.POST)
        if form.is_valid():
            invite_code = form.cleaned_data['invite_code']
            try:
                group = Group.objects.get(invite_code=invite_code)
                
                if group.matching_done:
                    messages.error(request, 'This group has already been matched. You cannot join.')
                    return redirect('join_group')
                
                Member.objects.create(group=group, user=request.user)
                messages.success(request, f'You joined "{group.name}"!')
                return redirect('group_detail', group_id=group.id)
            
            except Group.DoesNotExist:
                messages.error(request, 'Invalid invite code')
            except IntegrityError:
                messages.error(request, 'You are already a member of this group')
    else:
        form = JoinGroupForm()
    
    return render(request, 'groups/join.html', {'form': form})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    is_member = group.members.filter(user=request.user).exists()
    
    if not is_member:
        messages.error(request, 'You are not a member of this group')
        return redirect('home')
    
    members = group.members.select_related('user').all()
    user_member = group.members.get(user=request.user)
    
    # Check if user has a match
    try:
        match = Match.objects.get(group=group, giver=request.user)
    except Match.DoesNotExist:
        match = None
    
    context = {
        'group': group,
        'members': members,
        'user_member': user_member,
        'match': match,
        'is_host': group.host == request.user,
    }
    
    return render(request, 'groups/detail.html', context)

@login_required
def run_matching(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    if group.host != request.user:
        messages.error(request, 'Only the host can run matching')
        return redirect('group_detail', group_id=group.id)
    
    if group.matching_done:
        messages.warning(request, 'Matching has already been done for this group')
        return redirect('group_detail', group_id=group.id)
    
    member_count = group.members.count()
    if member_count < 2:
        messages.error(request, f'Need at least 2 members. Currently have {member_count}.')
        return redirect('group_detail', group_id=group.id)
    
    try:
        matcher = SecretSantaMatcher(group)
        matches = matcher.create_matches()
        
        # Send notifications asynchronously
        send_all_match_notifications.delay(group.id)
        
        messages.success(request, f'✅ Matching complete! {len(matches)} notifications are being sent.')
        return redirect('group_detail', group_id=group.id)
    
    except Exception as e:
        messages.error(request, f'Error during matching: {str(e)}')
        return redirect('group_detail', group_id=group.id)

@login_required
def my_match(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    try:
        match = Match.objects.select_related('receiver').get(group=group, giver=request.user)
        receiver_member = Member.objects.get(group=group, user=match.receiver)
        
        context = {
            'group': group,
            'match': match,
            'receiver_member': receiver_member,
        }
        
        return render(request, 'groups/my_match.html', context)
    
    except Match.DoesNotExist:
        messages.error(request, 'No match found. Matching may not have been done yet.')
        return redirect('group_detail', group_id=group.id)

@login_required
def edit_wishlist(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    member = get_object_or_404(Member, group=group, user=request.user)
    
    if request.method == 'POST':
        form = WishlistForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Wishlist updated!')
            return redirect('group_detail', group_id=group.id)
    else:
        form = WishlistForm(instance=member)
    
    return render(request, 'groups/edit_wishlist.html', {'form': form, 'group': group})


@login_required
def my_groups(request):
    """Display all groups the user is part of"""
    memberships = request.user.memberships.select_related('group').all()
    hosted_groups = request.user.hosted_groups.all()
    
    context = {
        'memberships': memberships,
        'hosted_groups': hosted_groups,
    }
    return render(request, 'groups/my_groups.html', context)