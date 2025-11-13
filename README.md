# Secret-Santa-Matcher

A web app that lets families, teams, or communities create Secret Santa groups.
Each member joins via an invite link, enters their details (and gift wishlist), and the app automatically pairs everyone — secretly — then emails or texts their match.


## ⚙️ 1. Core Features

### Feature	Description

- User Authentication	Users can sign up/log in or join via invite link
- Create a Group	A user (the “host”) creates a Secret Santa group
- Join a Group	Members join via a unique invite code or link
- Auto-Matching	Once all members join, system randomly pairs them
- Notifications	Each person receives an email/text with their match
- Gift Wishlist	Optional — users can write 3 gift ideas
- Reveal Mode (Optional)	After Christmas, everyone can see who their Santa was 🎅


## 2. Tech Stack

- Backend: Django + Django REST Framework

- Task Queue: Celery + Redis (for background match notifications)

- Database: PostgreSQL

- Email Service: Gmail SMTP

- Hosting: Render

- Frontend Django Templates
