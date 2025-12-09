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
    workout = models.OneToOneField(
        Workout, 
        on_delete=models.CASCADE, 
        related_name='route'
    )
    
    route_data = models.JSONField(
        help_text="Array of coordinate pairs [[lat, lng], ...]"
    )
    
    start_location = models.CharField(max_length=255, blank=True, null=True)
    end_location = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Route for {self.workout.title}"

    @property
    def total_points(self):
        return len(self.route_data) if self.route_data else 0

    
class AchievementPost(models.Model):
    """
    A post that appears on the public feed.
    Users can share workouts or manually post achievements.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="achievement_posts")
    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        related_name="shared_posts"
    )
    
    message = models.TextField(max_length=500, help_text="What do you want to share?")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Achievement by {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"
    
    def like_count(self):
        """Return the number of likes on this post"""
        return self.likes.count()
    
    def is_liked_by(self, user):
        """Check if a specific user has liked this post"""
        return self.likes.filter(user=user).exists()


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(
        AchievementPost,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} likes {self.post}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(
        AchievementPost,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    text = models.TextField(max_length=500, help_text="Add a comment")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"


class WorkoutWeather(models.Model):
    workout = models.OneToOneField(
        Workout,
        on_delete=models.CASCADE,
        related_name='weather'
    )
    
    # Weather data
    temperature = models.FloatField(help_text="Temperature in Celsius")
    feels_like = models.FloatField(help_text="Feels like temperature in Celsius", null=True, blank=True)
    humidity = models.IntegerField(help_text="Humidity percentage")
    weather_condition = models.CharField(max_length=100, help_text="e.g., Clear, Cloudy, Rain")
    weather_description = models.CharField(max_length=200, help_text="Detailed description")
    wind_speed = models.FloatField(help_text="Wind speed in m/s", null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Weather for {self.workout.title}: {self.temperature}°C, {self.weather_condition}"
    

class Milestone(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    milestone_type = models.CharField(max_length=50)
    threshold = models.FloatField()

    def __str__(self):
        return self.name
    
class UserMilestone(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    achieved_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'milestone')
