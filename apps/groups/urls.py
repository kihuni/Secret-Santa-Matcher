from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    path('create/', views.create_group, name='create'),
    path('join/', views.join_group, name='join'),
    path('<int:group_id>/', views.group_detail, name='detail'),
    path('<int:group_id>/match/', views.run_matching, name='run_matching'),
    path('<int:group_id>/my-match/', views.my_match, name='my_match'),
    path('<int:group_id>/wishlist/', views.edit_wishlist, name='edit_wishlist'),
    path('my-groups/', views.my_groups, name='my_groups'),
]