from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Workout, WorkoutRoute
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