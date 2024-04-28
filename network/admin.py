from django.contrib import admin

# import models here
from .models import User, Post

# Register your models here.

# Make custom UserAdmin class
class UserAdmin(admin.ModelAdmin):
    list_display = ("id","username","first_name","last_name","email")

# Register the user model in the standard way
admin.site.register(User, UserAdmin)


# The decorator registers the Post model and defines a custom PostAdmin 
# class to customize its appearance and behavior in the admin.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id","content","poster","created_at","likes_count")
    
    def likes_count(self, obj):
        return obj.likes.count() # Display the number of likes for each post
    
    
    