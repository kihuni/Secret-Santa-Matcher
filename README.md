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

<img width="1281" height="946" alt="image" src="https://github.com/user-attachments/assets/f586d9e2-dd22-490b-b312-83cb792ca2df" />
<img width="1281" height="946" alt="image" src="https://github.com/user-attachments/assets/16d13e55-26eb-4ffc-929b-a0f4be7c094e" />


<img width="1281" height="946" alt="image" src="https://github.com/user-attachments/assets/7e79ae2e-6233-47f8-b743-ec2705395d08" />
<img width="1281" height="946" alt="image" src="https://github.com/user-attachments/assets/0d496720-c6c1-469e-882a-5532f53e9cee" />

## 2. Tech Stack

- Backend: Django + Django REST Framework

- Task Queue: Celery + Redis (for background match notifications)

- Database: PostgreSQL

- Email Service: Gmail SMTP

- Hosting: Render

- Frontend Django Templates
