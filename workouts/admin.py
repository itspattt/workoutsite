from django.contrib import admin
from .models import Workout, WorkoutRoute, AchievementPost, Like, Comment, WorkoutWeather


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'workout_type', 'duration', 'distance', 'calories', 'workout_date']
    list_filter = ['workout_type', 'workout_date', 'user']
    search_fields = ['title', 'description', 'user__username']
    date_hierarchy = 'workout_date'


@admin.register(WorkoutRoute)
class WorkoutRouteAdmin(admin.ModelAdmin):
    list_display = ['workout', 'total_points', 'created_at']
    search_fields = ['workout__title', 'start_location', 'end_location']


@admin.register(AchievementPost)
class AchievementPostAdmin(admin.ModelAdmin):
    list_display = ['user', 'workout', 'created_at', 'like_count']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'message', 'workout__title']
    date_hierarchy = 'created_at'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__message']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'text', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'text', 'post__message']


@admin.register(WorkoutWeather)
class WorkoutWeatherAdmin(admin.ModelAdmin):
    list_display = ['workout', 'temperature', 'weather_condition', 'humidity', 'created_at']
    list_filter = ['weather_condition', 'created_at']
    search_fields = ['workout__title', 'weather_condition']

