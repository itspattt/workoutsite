from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Workout, WorkoutRoute, AchievementPost, Like, Comment, WorkoutWeather, Milestone, UserMilestone
from .forms import WorkoutForm, WorkoutRouteForm
import json
import requests
from django.conf import settings
from .utils import check_milestones

@login_required
def workout_list(request):
    """
    Display list of all workouts for the logged-in user.
    """
    workouts = Workout.objects.filter(user=request.user).order_by('-workout_date')

    return render(request, 'workouts/workout_list.html', {
        'workouts': workouts
    })


@login_required
def workout_detail(request, pk):
    """
    Display detailed view of a single workout, including route if available.
    """
    workout = get_object_or_404(Workout, pk=pk, user=request.user)
    has_route = hasattr(workout, 'route')
    
    return render(request, 'workouts/workout_detail.html', {
        'workout': workout,
        'has_route': has_route
    })


@login_required
def workout_create(request):
    """
    Create a new workout with manual logging.
    Feature: Manual workout logging (type, duration, calories, distance)
    """
    if request.method == 'POST':
        form = WorkoutForm(request.POST)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.user = request.user
            workout.save()
            messages.success(request, 'Workout logged successfully!')
            check_milestones(request.user)
            return redirect('workout_detail', pk=workout.pk)
    else:
        form = WorkoutForm()
    
    return render(request, 'workouts/workout_form.html', {
        'form': form,
        'title': 'Log New Workout'
    })


@login_required
def workout_edit(request, pk):
    """
    Edit an existing workout.
    """
    workout = get_object_or_404(Workout, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = WorkoutForm(request.POST, instance=workout)
        if form.is_valid():
            form.save()
            messages.success(request, 'Workout updated successfully!')
            return redirect('workout_detail', pk=workout.pk)
    else:
        form = WorkoutForm(instance=workout)
    
    return render(request, 'workouts/workout_form.html', {
        'form': form,
        'title': 'Edit Workout',
        'workout': workout
    })


@login_required
def workout_delete(request, pk):
    """
    Delete a workout.
    """
    workout = get_object_or_404(Workout, pk=pk, user=request.user)
    
    if request.method == 'POST':
        workout.delete()
        messages.success(request, 'Workout deleted successfully!')
        return redirect('workout_list')
    
    return render(request, 'workouts/workout_confirm_delete.html', {
        'workout': workout
    })


@login_required
def workout_add_route(request, pk):
    """
    Add or edit a route for an existing workout.
    Feature: Record workout route on a map for visualization
    """
    workout = get_object_or_404(Workout, pk=pk, user=request.user)
    
    try:
        route = workout.route
        is_edit = True
    except WorkoutRoute.DoesNotExist:
        route = None
        is_edit = False
    
    if request.method == 'POST':
        if is_edit:
            form = WorkoutRouteForm(request.POST, instance=route)
        else:
            form = WorkoutRouteForm(request.POST)
        
        if form.is_valid():
            route = form.save(commit=False)
            route.workout = workout
            route.save()
            messages.success(request, 'Route saved successfully!')
            return redirect('workout_detail', pk=workout.pk)
    else:
        if is_edit:
            form = WorkoutRouteForm(instance=route)
        else:
            form = WorkoutRouteForm()
    
    # Prepare initial route data for map
    initial_route = None
    if is_edit and route.route_data:
        initial_route = json.dumps(route.route_data)
    
    return render(request, 'workouts/workout_route_form.html', {
        'form': form,
        'workout': workout,
        'initial_route': initial_route,
        'is_edit': is_edit
    })


@login_required
def workout_route_delete(request, pk):
    """
    Delete a workout route.
    """
    workout = get_object_or_404(Workout, pk=pk, user=request.user)
    
    try:
        route = workout.route
    except WorkoutRoute.DoesNotExist:
        messages.error(request, 'No route found for this workout.')
        return redirect('workout_detail', pk=workout.pk)
    
    if request.method == 'POST':
        route.delete()
        messages.success(request, 'Route deleted successfully!')
        return redirect('workout_detail', pk=workout.pk)
    
    return render(request, 'workouts/workout_route_confirm_delete.html', {
        'workout': workout,
        'route': route
    })

@login_required
def progress_dashboard(request):
    """
    Displays the progress dashboard with charts.
    """
    return render(request, 'workouts/progress_dashboard.html')

@login_required
def progress_data(request):
    """
    Returns aggregated workout data for charts in JSON format.
    """

    workouts = Workout.objects.filter(user=request.user).order_by('workout_date')

    dates = [w.workout_date.strftime("%Y-%m-%d") for w in workouts]
    duration = [w.duration for w in workouts]
    calories = [w.calories or 0 for w in workouts]
    distance = [float(w.distance) if w.distance else 0 for w in workouts]

    type_counts = (
        workouts.values('workout_type')
                .annotate(total=Count('id'))
                .order_by('workout_type')
    )

    type_labels = [item['workout_type'] for item in type_counts]
    type_values = [item['total'] for item in type_counts]

    return JsonResponse({
        "dates": dates,
        "duration": duration,
        "calories": calories,
        "distance": distance,
        "type_labels": type_labels,
        "type_values": type_values,
    })

@login_required
def feed_view(request):
    posts = AchievementPost.objects.select_related("user", "workout").prefetch_related("likes", "comments__user")
    
    # Add is_liked attribute to each post for the current user
    for post in posts:
        post.user_has_liked = post.is_liked_by(request.user)
    
    return render(request, "workouts/feed.html", {"posts": posts})

# @login_required
# def create_feed_post(request, workout_id=None):
    workout = None

    if workout_id:
        workout = get_object_or_404(Workout, pk=workout_id, user=request.user)

        already_shared = AchievementPost.objects.filter(
            user=request.user, workout=workout
        ).exists()

        if already_shared:
            messages.error(request, "You have already shared this workout.")
            return redirect('public_workout_detail', workout.pk)

    if request.method == "POST":
        message = request.POST.get("message")

        if not message:
            messages.error(request, "Message cannot be empty.")
            return redirect(request.path)

        AchievementPost.objects.create(
            user=request.user,
            workout=workout,
            message=message
        )

        messages.success(request, "Achievement posted to feed!")
        return redirect("feed")

    return render(request, "workouts/create_feed_post.html", {
        "workout": workout
    })

@login_required
def create_feed_post(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id, user=request.user)

    # Prevent duplicate sharing
    already_shared = AchievementPost.objects.filter(
        user=request.user, workout=workout
    ).exists()

    if already_shared:
        messages.error(request, "You have already shared this workout.")
        return redirect('public_workout_detail', workout.pk)

    if request.method == "POST":
        message = request.POST.get("message")

        if not message:
            messages.error(request, "Message cannot be empty.")
            return redirect(request.path)

        AchievementPost.objects.create(
            user=request.user,
            workout=workout,
            message=message
        )

        messages.success(request, "Achievement posted to feed!")
        return redirect("feed")

    return render(request, "workouts/create_feed_post.html", {
        "workout": workout
    })

@login_required
def public_workout_detail(request, pk):
    workout = get_object_or_404(Workout, pk=pk)

    is_shared = workout.shared_posts.exists()

    if not workout.shared_posts.exists() and not request.user.is_staff:
        raise Http404("Workout not shared publicly")

    has_route = hasattr(workout, 'route')

    is_owner = (workout.user == request.user)

    return render(request, "workouts/public_workout_detail.html", {
        "workout": workout,
        "has_route": has_route,
        "is_owner": is_owner, 
    })

@login_required
def edit_feed_post(request, post_id):
    post = get_object_or_404(AchievementPost, pk=post_id)

    if post.user != request.user:
        raise Http404("You are not allowed to edit this post.")

    if request.method == "POST":
        message = request.POST.get("message")

        if not message:
            messages.error(request, "Message cannot be empty.")
            return redirect(request.path)

        post.message = message
        post.save()
        messages.success(request, "Achievement updated!")
        return redirect("feed")

    return render(request, "workouts/edit_feed_post.html", {
        "post": post
    })

@login_required
def delete_feed_post(request, post_id):
    post = get_object_or_404(AchievementPost, pk=post_id)

    if post.user != request.user:
        raise Http404("You are not allowed to delete this post.")

    if request.method == "POST":
        post.delete()
        messages.success(request, "Achievement deleted.")
        return redirect("feed")

    return render(request, "workouts/delete_feed_post.html", {
        "post": post
    })


@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(AchievementPost, pk=post_id)
    
    existing_like = Like.objects.filter(user=request.user, post=post).first()
    
    if existing_like:
        existing_like.delete()
        liked = False
        message = "Like removed"
    else:
        Like.objects.create(user=request.user, post=post)
        liked = True
        message = "Post liked!"
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'liked': liked,
            'like_count': post.like_count(),
            'message': message
        })
    
    messages.success(request, message)
    return redirect('feed')


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(AchievementPost, pk=post_id)
    
    if request.method == "POST":
        comment_text = request.POST.get("comment_text", "").strip()
        
        if not comment_text:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Comment cannot be empty'})
            messages.error(request, "Comment cannot be empty.")
            return redirect("feed")
        
        comment = Comment.objects.create(
            user=request.user,
            post=post,
            text=comment_text
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.id,
                    'user': comment.user.username,
                    'text': comment.text,
                    'created_at': comment.created_at.strftime('%b %d, %Y %I:%M %p'),
                    'is_owner': comment.user == request.user
                }
            })
        
        messages.success(request, "Comment added!")
    
    return redirect("feed")


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    
    if comment.user != request.user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Not authorized'})
        raise Http404("You are not allowed to delete this comment.")
    
    comment.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Comment deleted'})
    
    messages.success(request, "Comment deleted.")
    return redirect("feed")


@login_required
def fetch_weather(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id, user=request.user)
    
    if hasattr(workout, 'weather'):
        messages.info(request, "Weather data already exists for this workout.")
        return redirect('workout_detail', pk=workout_id)
    
    latitude = None
    longitude = None
    
    if hasattr(workout, 'route') and workout.route.route_data:
        route_data = workout.route.route_data
        if route_data and len(route_data) > 0:
            latitude = route_data[0][0]
            longitude = route_data[0][1]
    
    if not latitude or not longitude:
        latitude = 37.7749
        longitude = -122.4194
        messages.warning(request, "No route location found. Using default location for weather data.")

    api_key = getattr(settings, 'OPENWEATHERMAP_API_KEY', None)
    
    if not api_key:
        messages.error(request, "Weather API key not configured. Please add OPENWEATHERMAP_API_KEY to settings.")
        return redirect('workout_detail', pk=workout_id)
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': latitude,
            'lon': longitude,
            'appid': api_key,
            'units': 'metric'  # Celsius
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        WorkoutWeather.objects.create(
            workout=workout,
            temperature=data['main']['temp'],
            feels_like=data['main'].get('feels_like'),
            humidity=data['main']['humidity'],
            weather_condition=data['weather'][0]['main'],
            weather_description=data['weather'][0]['description'],
            wind_speed=data['wind'].get('speed'),
            latitude=latitude,
            longitude=longitude
        )
        
        messages.success(request, "Weather data added successfully!")
        
    except requests.RequestException as e:
        messages.error(request, f"Failed to fetch weather data: {str(e)}")
    except KeyError as e:
        messages.error(request, f"Invalid weather data received: {str(e)}")
    
    return redirect('workout_detail', pk=workout_id)


@login_required
def milestones(request):
    user = request.user

    # Get all milestones and mark which are unlocked
    all_milestones = Milestone.objects.all()
    unlocked_ids = UserMilestone.objects.filter(user=user).values_list('milestone_id', flat=True)

    # Build a list for template with status
    milestones_with_status = []
    for m in all_milestones:
        milestones_with_status.append({
            "name": m.name,
            "description": m.description,
            "threshold": m.threshold,
            "type": m.milestone_type,
            "unlocked": m.id in unlocked_ids
        })

    context = {
        "milestones": milestones_with_status
    }

    UserMilestone.objects.filter(user=request.user, seen=False).update(seen=True)

    return render(request, "workouts/milestones.html", context)