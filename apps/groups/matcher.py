import random
from django.db import transaction
from .models import Match, Member

class SecretSantaMatcher:
    def __init__(self, group):
        self.group = group
    
    def create_matches(self):
        """Create Secret Santa matches for a group"""
        members = list(self.group.members.all())
        
        if len(members) < 2:
            raise ValueError("Need at least 2 members to create matches")
        
        # Get list of users
        users = [m.user for m in members]
        receivers = users.copy()
        
        # Shuffle receivers
        random.shuffle(receivers)
        
        # Ensure no one gets themselves
        for i, giver in enumerate(users):
            if giver == receivers[i]:
                # Swap with next person (wrap around if at end)
                j = (i + 1) % len(receivers)
                receivers[i], receivers[j] = receivers[j], receivers[i]
        
        # Create matches in database
        with transaction.atomic():
            # Delete old matches if rerunning
            Match.objects.filter(group=self.group).delete()
            
            # Create new matches
            matches = []
            for giver, receiver in zip(users, receivers):
                match = Match(
                    group=self.group,
                    giver=giver,
                    receiver=receiver
                )
                matches.append(match)
            
            Match.objects.bulk_create(matches)
            
            # Mark group as matched
            self.group.matching_done = True
            self.group.save()
        
        return matches