
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("new-post", views.new_post, name="new-post"),
    path("follow/<str:username>", views.follow_user, name="follow_user"),
    path("following", views.following_posts, name="following_posts"),
    path("update-post", views.update_post, name="update_post"),
    path("like-post", views.like_post, name="like_post"),
]
