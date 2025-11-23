from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    path('', views.my_groups, name='my_groups'),
    path('create/', views.create_group, name='create'),
    path('join/', views.join_group, name='join'),
    path('join/<str:invite_code>/', views.join_group, name='join_with_code'),
    
    # Group-specific pages (using invite_code for cleaner URLs)
    path('<str:invite_code>/', views.group_detail, name='detail'),
    path('<str:invite_code>/match/', views.run_matching, name='run_matching'),
    path('<str:invite_code>/my-match/', views.my_match, name='my_match'),
    path('<str:invite_code>/wishlist/', views.edit_wishlist, name='edit_wishlist'),
    path('<str:invite_code>/leave/', views.leave_group, name='leave'),
    path('<str:invite_code>/delete/', views.delete_group, name='delete'),
]