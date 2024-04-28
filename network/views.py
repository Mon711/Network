from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from .models import User, Post


def index(request):
    # Retrieve all posts from db
    # Order posts by descending created_at
    posts = Post.objects.order_by("-created_at") # "-" to specify descending order.
    
    # Initialise Paginator object by paginating the posts
    # Show 10 posts per page
    paginator = Paginator(posts, 10)
    
    # get value of the "page" parameter from the request's query string
    page = request.GET.get("page")
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page_obj = paginator.page(1)
    except EmptyPage:
        # if page is out of range, deliver last page
        page_obj = paginator.page(paginator.num_pages)
    
    
    context = {
        "page_obj": page_obj,
        "title": "All Posts"
        }
    return render(request, "network/index.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        if request.user.is_authenticated:
            return redirect("profile", username=request.user.username)
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return redirect("index")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match.",
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken.",
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
            })
            
        login(request, user)
        
        return redirect("index")
    else:
        if request.user.is_authenticated:
            return redirect("profile", username=request.user.username)
        return render(request, "network/register.html")


def profile(request, username):
    # Retrieve user profile
    profile_user = User.objects.get(username=username)
    
    # Retrieve current user
    current_user = request.user
    
    # Fetch posts by the user
    posts = profile_user.posts_created.order_by("-created_at")
    
    # Check if the profile being viewed belongs to the signed-in user
    is_own_profile = current_user == profile_user


    if not is_own_profile:
        # Check if the current user is following the profile page user
        if current_user in profile_user.followers.all():
            is_following = True
        else:
            is_following = False
    else:
        # for cases where either profile being viewed belongs to the signed-in user
        # or no user is signed-in
        is_following = None
        
        
    
    context = {
        "profile_user": profile_user,
        "posts": posts,
        "is_own_profile": is_own_profile,
        "is_following": is_following
    }
    
    return render(request, "network/profile.html", context)

@login_required
def new_post(request):
    if request.method == "POST":
        # Get the content from the form and the logged in user
        content = request.POST["content"]
        poster = request.user
        
        # Create a new Post instance and save it to the db
        post = Post(content=content, poster=poster)
        post.save()
        
        # Add a success message
        messages.success(request, "Post Published!!")
        
        # Redirect to All Posts page
        return redirect("index")
        
    else:
        return render(request, "network/new_post.html")
    
    
def follow_user(request, username):
    # Get the users involved
    current_user = request.user
    profile_user = User.objects.get(username=username)
    
    # Toggle the 'follow' relationship
    if current_user in profile_user.followers.all():
        current_user.following.remove(profile_user)
    else:
        current_user.following.add(profile_user)
    
    # Redirect to profile page
    return redirect("profile", username=username)
    

@login_required
def following_posts(request):
    # Get the current user
    current_user = request.user
    
    # Get list of people user is following
    following_users = current_user.following.all()
    
    # Get all posts created by those users
    # __: Django uses double underscores (__) to traverse relationships between models
    # poster Field: poster refers to the foreign key field in the Post model that links back to the User model
    # in Operator: This operator checks if a value is present within a collection of values.
    following_posts = Post.objects.filter(poster__in=following_users).order_by("-created_at")
    
    paginator = Paginator(following_posts, 10)
    page = request.GET.get("page")
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        "page_obj": page_obj,
        "title": "Posts by users you Follow"
    }
    
    return render(request, "network/index.html", context)


@csrf_exempt
def update_post(request):
    if request.method == "POST":
        # Load the JSON data sent in the POST request
        data = json.loads(request.body)
        
        # Extract the post ID and new content from the data
        post_id = data["post_id"]
        new_content = data["new_content"]
        
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "User not authenticated"})
        
        # Check if the user is the author of the post
        try:
            post = Post.objects.get(id=post_id, poster=request.user)
        except Post.DoesNotExist:
            return JsonResponse({"status": "error", "message": "User not authorised to edit this post"})
        
        # Update the post content in the database
        post.content = new_content
        post.save()
        
        return JsonResponse({"status": "success"})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"})
    
    
@csrf_exempt
def like_post(request):
    if request.method == "POST":
        # Load the json data sent in the POST request
        data = json.loads(request.body)
        
        # Extract the post ID from the data
        postId = data["post_id"]
        
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "User not authorised to like posts"})
        else:
            user = request.user
        
        # Check if post is valid
        try:
            post = Post.objects.get(id=postId)
        except Post.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Post doesn't exist"})
        
        # Update the likes count 
        # Update "Like"/"Unlike" button style
        if user in post.likes.all():
            post.likes.remove(user)
            text = ["btn-outline-primary", "btn-primary", "Like"]
        else:
            post.likes.add(user)
            text = ["btn-primary", "btn-outline-primary", "Unlike"]
            
        return JsonResponse(
            {
                "likes_count": post.likes.count(),
                "text": text
            }
        )
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"})
