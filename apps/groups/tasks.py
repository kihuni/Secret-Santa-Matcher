from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Match, Member

@shared_task
def send_match_notification(match_id):
    """Send email notification to a giver about their match"""
    try:
        match = Match.objects.select_related('giver', 'receiver', 'group').get(id=match_id)
        
        # Get receiver's wishlist
        receiver_member = Member.objects.get(group=match.group, user=match.receiver)
        wishlist = receiver_member.wishlist if receiver_member.wishlist else "No wishlist provided"
        
        subject = f"🎅 Your Secret Santa Match for {match.group.name}"
        message = f"""
Hi {match.giver.first_name or match.giver.username}!

You're the Secret Santa for: {match.receiver.first_name or match.receiver.username}

Their Wishlist:
{wishlist}

Budget: ${match.group.budget_limit if match.group.budget_limit else 'No limit set'}

Remember - keep it a secret! 🤫

Happy gifting!
- Secret Santa Matcher
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [match.giver.email],
            fail_silently=False,
        )
        
        match.notification_sent = True
        match.save()
        
        return f"Notification sent to {match.giver.email}"
    
    except Exception as e:
        return f"Error sending notification: {str(e)}"

@shared_task
def send_all_match_notifications(group_id):
    """Send notifications to all members of a group"""
    from .models import Group
    
    group = Group.objects.get(id=group_id)
    matches = group.matches.all()
    
    for match in matches:
        send_match_notification.delay(match.id)
    
    return f"Queued {matches.count()} notifications for {group.name}"