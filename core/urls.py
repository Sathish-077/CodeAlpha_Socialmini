from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.feed_view, name='feed'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Posts
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),

    # Comments
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    # Follow
    path('follow/<str:username>/', views.toggle_follow, name='toggle_follow'),

    # Profiles
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/edit/me/', views.edit_profile, name='edit_profile'),

    # Search & Explore
    path('search/', views.search_view, name='search'),
    path('explore/', views.explore_view, name='explore'),
]
