from django.contrib.auth.models import AbstractUser
from django.db import models


# 1. ManyToManyField("self"): This creates a many-to-many relationship between users directly 
#    within the User model, eliminating the need for a separate Follow model.

# 2. symmetrical=False: This ensures the relationship is not automatically reciprocal 
#    (i.e., if user A follows user B, it doesn't automatically mean B follows A).

# 3. related_name="followers": This provides a clear way to access a user's followers 
#    using user.followers.all().
class User(AbstractUser):
    following = models.ManyToManyField("self", symmetrical=False, related_name="followers")
    def __str__(self):
        return self.username
    

 
# Using likes field in the Post model eliminates the need for a separate Like model, 
# simplifying the database structure and reducing queries.
class Post(models.Model):
	content = models.TextField()
	poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts_created")
	created_at = models.DateTimeField(auto_now_add=True)
	likes = models.ManyToManyField(User, related_name="liked_posts")
    

