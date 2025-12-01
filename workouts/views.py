from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Workout, WorkoutRoute, AchievementPost
from .forms import WorkoutForm, WorkoutRouteForm
import json

@login_required
def workout_list(request):
    """
    Display list of all workouts for the logged-in user.
    """
    workouts = Workout.objects.filter(user=request.user)
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
    
    # Check if route already exists
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

    # Line chart data
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
    """
    Public feed showing all user achievements.
    """
    posts = AchievementPost.objects.select_related("user", "workout")
    return render(request, "workouts/feed.html", {"posts": posts})

# @login_required
# def create_feed_post(request, workout_id=None):
    """
    Create a new achievement post, optionally tied to a workout.
    """
    workout = None

    if workout_id:
        workout = get_object_or_404(Workout, pk=workout_id, user=request.user)

        # ⭐ Prevent duplicate sharing
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
    """
    Create a new achievement post tied to a specific workout.
    Users cannot create posts unrelated to workouts.
    """
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
    """
    Public-safe view of a workout shared through the feed.
    Anyone can view this if the workout is associated with an AchievementPost.
    """
    workout = get_object_or_404(Workout, pk=pk)

    # Check if this workout was shared publicly
    is_shared = workout.shared_posts.exists()

    if not workout.shared_posts.exists() and not request.user.is_staff:
        # Do NOT leak existence or privacy — return 404
        raise Http404("Workout not shared publicly")

    has_route = hasattr(workout, 'route')

    # Determine if current user owns the workout
    is_owner = (workout.user == request.user)

    return render(request, "workouts/public_workout_detail.html", {
        "workout": workout,
        "has_route": has_route,
        "is_owner": is_owner,  # Used to show edit buttons only for owner
    })

@login_required
def edit_feed_post(request, post_id):
    post = get_object_or_404(AchievementPost, pk=post_id)

    # Only post owner can edit
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

    # Only owner can delete
    if post.user != request.user:
        raise Http404("You are not allowed to delete this post.")

    if request.method == "POST":
        post.delete()
        messages.success(request, "Achievement deleted.")
        return redirect("feed")

    return render(request, "workouts/delete_feed_post.html", {
        "post": post
    })