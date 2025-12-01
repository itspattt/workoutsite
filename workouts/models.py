# workout/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Workout(models.Model):
    """
    Model for manual workout logging.
    Tracks workout type, duration, calories, and distance.
    """
    WORKOUT_TYPES = [
        ('running', 'Running'),
        ('cycling', 'Cycling'),
        ('swimming', 'Swimming'),
        ('walking', 'Walking'),
        ('hiking', 'Hiking'),
        ('gym', 'Gym/Strength Training'),
        ('yoga', 'Yoga'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    workout_type = models.CharField(max_length=50, choices=WORKOUT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Core workout metrics
    duration = models.IntegerField(help_text="Duration in minutes")
    calories = models.IntegerField(help_text="Calories burned", null=True, blank=True)
    distance = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        help_text="Distance in kilometers",
        null=True,
        blank=True
    )
    
    # Timestamps
    workout_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-workout_date']
        
    def __str__(self):
        return f"{self.title} - {self.workout_type} ({self.workout_date.strftime('%Y-%m-%d')})"


class WorkoutRoute(models.Model):
    """
    Model for storing workout route data (GPS coordinates).
    Allows users to visualize their workout routes on a map.
    """
    workout = models.OneToOneField(
        Workout, 
        on_delete=models.CASCADE, 
        related_name='route'
    )
    
    # Store route as JSON array of [lat, lng] coordinates
    route_data = models.JSONField(
        help_text="Array of coordinate pairs [[lat, lng], ...]"
    )
    
    # Additional route metadata
    start_location = models.CharField(max_length=255, blank=True, null=True)
    end_location = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Route for {self.workout.title}"

    @property
    def total_points(self):
        """Return the number of GPS points in the route"""
        return len(self.route_data) if self.route_data else 0

    
class AchievementPost(models.Model):
    """
    A post that appears on the public feed.
    Users can share workouts or manually post achievements.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="achievement_posts")
    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,   # delete post if workout is deleted
        related_name="shared_posts"
    )
    
    message = models.TextField(max_length=500, help_text="What do you want to share?")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Achievement by {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"
    

    
