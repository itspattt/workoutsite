from django.contrib import admin
from .models import Workout, WorkoutRoute


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

