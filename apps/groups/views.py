from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import Http404
from .models import Group, Member, Match
from .forms import GroupCreateForm, JoinGroupForm, WishlistForm
from .matcher import SecretSantaMatcher
# from .tasks import send_all_match_notifications  # Uncomment when Celery is set up

@login_required
def create_group(request):
    """Create a new Secret Santa group"""
    if request.method == 'POST':
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.host = request.user
            group.save()
            
            # Auto-join creator as member
            Member.objects.create(group=group, user=request.user)
            
            messages.success(
                request, 
                f'🎉 Group "{group.name}" created! Share this invite code with your participants: {group.invite_code}'
            )
            return redirect('groups:detail', invite_code=group.invite_code)
    else:
        form = GroupCreateForm()
    
    return render(request, 'groups/create.html', {'form': form})

@login_required
def join_group(request, invite_code=None):
    """Join an existing group via invite code"""
    # Pre-fill form if invite_code is in URL
    initial = {'invite_code': invite_code} if invite_code else {}
    
    if request.method == 'POST':
        form = JoinGroupForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['invite_code'].upper().strip()
            try:
                group = Group.objects.get(invite_code=code)
                
                if group.matching_done:
                    messages.error(request, '🚫 This group has already done their Secret Santa matching. You cannot join.')
                    return redirect('groups:join')
                
                # Check if already a member
                if Member.objects.filter(group=group, user=request.user).exists():
                    messages.info(request, f'You are already a member of "{group.name}"!')
                    return redirect('groups:detail', invite_code=group.invite_code)
                
                Member.objects.create(group=group, user=request.user)
                messages.success(request, f'🎄 Welcome! You joined "{group.name}"!')
                return redirect('groups:detail', invite_code=group.invite_code)
            
            except Group.DoesNotExist:
                messages.error(request, '❌ Invalid invite code. Please check and try again.')
    else:
        form = JoinGroupForm(initial=initial)
    
    return render(request, 'groups/join.html', {'form': form})

@login_required
def group_detail(request, invite_code):
    """View group details - 'Santa's Workshop' page"""
    group = get_object_or_404(Group, invite_code=invite_code)
    
    # Check membership
    try:
        user_member = Member.objects.get(group=group, user=request.user)
    except Member.DoesNotExist:
        messages.error(request, 'You need to join this group first!')
        return redirect('groups:join', invite_code=invite_code)
    
    members = group.members.select_related('user').all()
    
    # Check if user has a match
    match = Match.objects.filter(group=group, giver=request.user).first()
    
    # Count members with wishlists
    wishlist_count = members.exclude(wishlist='').exclude(wishlist__isnull=True).count()
    
    context = {
        'group': group,
        'members': members,
        'user_member': user_member,
        'match': match,
        'is_host': group.host == request.user,
        'member_count': members.count(),
        'wishlist_count': wishlist_count,
        'ready_to_match': members.count() >= 2 and not group.matching_done,
    }
    
    return render(request, 'groups/detail.html', context)

@login_required
def run_matching(request, invite_code):
    """Run the Secret Santa matching algorithm - Host only"""
    group = get_object_or_404(Group, invite_code=invite_code)
    
    if request.method != 'POST':
        return redirect('groups:detail', invite_code=invite_code)
    
    if group.host != request.user:
        messages.error(request, '🚫 Only the group host can run the matching!')
        return redirect('groups:detail', invite_code=invite_code)
    
    if group.matching_done:
        messages.warning(request, 'Matching has already been done for this group.')
        return redirect('groups:detail', invite_code=invite_code)
    
    member_count = group.members.count()
    if member_count < 2:
        messages.error(request, f'❌ Need at least 2 participants. Currently have {member_count}.')
        return redirect('groups:detail', invite_code=invite_code)
    
    try:
        matcher = SecretSantaMatcher(group)
        matches = matcher.create_matches()
        
        # TODO: Uncomment when Celery is configured
        # send_all_match_notifications.delay(group.id)
        
        messages.success(
            request, 
            f'🎅 Ho ho ho! Matching complete! {len(matches)} Secret Santas have been assigned. '
            f'Everyone can now view their match!'
        )
        return redirect('groups:detail', invite_code=invite_code)
    
    except Exception as e:
        messages.error(request, f'❌ Error during matching: {str(e)}')
        return redirect('groups:detail', invite_code=invite_code)

@login_required
def my_match(request, invite_code):
    """View your Secret Santa assignment - 'Your Secret Mission' page"""
    group = get_object_or_404(Group, invite_code=invite_code)
    
    # Verify membership
    if not Member.objects.filter(group=group, user=request.user).exists():
        raise Http404("You are not a member of this group")
    
    try:
        match = Match.objects.select_related('receiver').get(group=group, giver=request.user)
        receiver_member = Member.objects.get(group=group, user=match.receiver)
        
        context = {
            'group': group,
            'match': match,
            'receiver': match.receiver,
            'receiver_member': receiver_member,
        }
        
        return render(request, 'groups/my_match.html', context)
    
    except Match.DoesNotExist:
        messages.info(request, '⏳ Matching hasn\'t been done yet. Ask your host to run the matching!')
        return redirect('groups:detail', invite_code=invite_code)

@login_required
def edit_wishlist(request, invite_code):
    """Edit your gift wishlist"""
    group = get_object_or_404(Group, invite_code=invite_code)
    member = get_object_or_404(Member, group=group, user=request.user)
    
    if request.method == 'POST':
        form = WishlistForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Your wishlist has been saved! Your Secret Santa will appreciate the hints!')
            return redirect('groups:detail', invite_code=invite_code)
    else:
        form = WishlistForm(instance=member)
    
    return render(request, 'groups/edit_wishlist.html', {'form': form, 'group': group})

@login_required
def my_groups(request):
    """View all groups the user is part of - 'My Santa Groups' page"""
    memberships = request.user.memberships.select_related('group', 'group__host').all()
    hosted_groups = request.user.hosted_groups.prefetch_related('members').all()
    
    context = {
        'memberships': memberships,
        'hosted_groups': hosted_groups,
        'total_count': memberships.count(),
    }
    return render(request, 'groups/my_groups.html', context)

@login_required
def leave_group(request, invite_code):
    """Leave a group (cannot leave if matching is done or if you're the host)"""
    group = get_object_or_404(Group, invite_code=invite_code)
    
    if request.method != 'POST':
        return redirect('groups:detail', invite_code=invite_code)
    
    if group.host == request.user:
        messages.error(request, '🚫 As the host, you cannot leave. You can delete the group instead.')
        return redirect('groups:detail', invite_code=invite_code)
    
    if group.matching_done:
        messages.error(request, '🚫 Cannot leave after matching has been done. Someone is counting on you!')
        return redirect('groups:detail', invite_code=invite_code)
    
    try:
        member = Member.objects.get(group=group, user=request.user)
        member.delete()
        messages.success(request, f'You have left "{group.name}".')
        return redirect('groups:my_groups')
    except Member.DoesNotExist:
        return redirect('home')

@login_required  
def delete_group(request, invite_code):
    """Delete a group - Host only, before matching"""
    group = get_object_or_404(Group, invite_code=invite_code)
    
    if request.method != 'POST':
        return redirect('groups:detail', invite_code=invite_code)
    
    if group.host != request.user:
        messages.error(request, '🚫 Only the host can delete this group.')
        return redirect('groups:detail', invite_code=invite_code)
    
    if group.matching_done:
        messages.error(request, '🚫 Cannot delete a group after matching. People are expecting gifts!')
        return redirect('groups:detail', invite_code=invite_code)
    
    group_name = group.name
    group.delete()
    messages.success(request, f'Group "{group_name}" has been deleted.')
    return redirect('groups:my_groups')
