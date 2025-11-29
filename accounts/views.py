# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta
from workouts.models import Workout, WorkoutRoute

KG_TO_LBS = 2.20462
CM_TO_INCH = 1 / 2.54  # cm * CM_TO_INCH = inches

def login_view(request):
    print("METHOD:", request.method, "POST:", request.POST)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Please enter both username and password")
            return redirect('login')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # ✅ only call login if user exists
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')
    else:
        # GET request -> just show the form
        return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)  # log the user out
    return redirect('home')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Basic validation
        if not username or not password1 or not password2:
            messages.error(request, "Please fill out all fields")
            return redirect('signup')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')

        # Create the user
        user = User.objects.create_user(username=username, password=password1)
        user.save()

        # Automatically log the user in
        login(request, user)
        return redirect('workout_list')

    else:
        return render(request, 'accounts/signup.html')

# @login_required
# def profile_update_view(request):
#     profile = request.user.profile

#     if request.method == "POST":
#         user_form = UserUpdateForm(request.POST, instance=request.user)
#         profile_form = ProfileUpdateForm(request.POST, instance=profile)

#         if user_form.is_valid() and profile_form.is_valid():
#             cd = profile_form.cleaned_data

#             unit_pref = cd["unit_preference"]  # 'metric' or 'imperial'
#             age = cd["age"]
#             weight = cd["weight"]
#             height = cd["height"]

#             # Convert FROM current unit_pref TO metric for storage
#             if unit_pref == "imperial":
#                 # lbs → kg
#                 weight_kg = weight / KG_TO_LBS if weight is not None else None
#                 # inches → cm
#                 height_cm = height * 2.54 if height is not None else None
#             else:
#                 # already metric
#                 weight_kg = weight
#                 height_cm = height

#             profile.age = age
#             profile.weight = weight_kg
#             profile.height = height_cm
#             profile.unit_preference = unit_pref
#             profile.save()

#             user_form.save()
#             messages.success(request, "Profile updated successfully!")
#             return redirect("profile_update_view")
#     else:
#         # SHOW values in selected units
#         unit_pref = profile.unit_preference or "metric"

#         if unit_pref == "imperial":
#             display_weight = (
#                 profile.weight * KG_TO_LBS if profile.weight is not None else None
#             )
#             display_height = (
#                 profile.height * CM_TO_INCH if profile.height is not None else None
#             )
#         else:
#             display_weight = profile.weight
#             display_height = profile.height

#         user_form = UserUpdateForm(instance=request.user)
#         profile_form = ProfileUpdateForm(
#             instance=profile,
#             initial={
#                 "weight": display_weight,
#                 "height": display_height,
#                 "unit_preference": unit_pref,
#             },
#         )

#     return render(
#         request,
#         "accounts/profile_update.html",
#         {
#             "user_form": user_form,
#             "profile_form": profile_form,
#         },
#     )

@login_required
def profile_update_view(request):
    profile = request.user.profile

    KG_TO_LBS = 2.20462
    CM_TO_IN = 0.393701

    feet = None
    inches = None

    if request.method == "POST":
        # Make a mutable copy of POST data
        post_data = request.POST.copy()

        # TEMP height hack (so form passes validation)
        if post_data.get("height_unit_preference") == "ft_in":
            post_data["height"] = "0"
        
        # Ensure distance unit preference is included in POST data
        if "distance_unit_preference" not in post_data or not post_data["distance_unit_preference"]:
            post_data["distance_unit_preference"] = profile.distance_unit_preference

        user_form = UserUpdateForm(post_data, instance=request.user)
        form = ProfileUpdateForm(post_data, instance=profile)

            # 👉 INSERT DEBUG BLOCK HERE 👇
        if not form.is_valid():
            print("FORM ERRORS --->", form.errors)

        if user_form.is_valid() and form.is_valid():
            data = form.cleaned_data

            # --- AGE ---
            profile.age = data["age"]

            # --- WEIGHT ---
            weight_input = data["weight"]
            weight_unit = data["weight_unit_preference"]

            if weight_input is not None:
                if weight_unit == "lbs":
                    profile.weight = weight_input / KG_TO_LBS   # store as kg
                else:
                    profile.weight = weight_input               # already kg

            profile.weight_unit_preference = weight_unit

            # --- HEIGHT ---
            height_unit = data["height_unit_preference"]

            if height_unit == "ft_in":
                feet = request.POST.get("height_feet")
                inches = request.POST.get("height_inches")

                feet = int(feet) if feet else 0
                inches = float(inches) if inches else 0

                total_cm = (feet * 30.48) + (inches * 2.54)
                profile.height = total_cm

            else:
                # metric cm
                profile.height = data["height"]

            profile.height_unit_preference = height_unit

            # --- DISTANCE (for later workout section) ---
            profile.distance_unit_preference = data["distance_unit_preference"]

            # Save both profile + user
            profile.save()
            user_form.save()

            print(">>> SUCCESS MESSAGE TRIGGERED <<<")
            messages.success(request, "Profile updated!")
            return redirect("profile_update")

    else:
        # PRE-FILL FIELDS BASED ON UNIT PREFERENCE

        # weight
        if profile.weight_unit_preference == "lbs" and profile.weight is not None:
            display_weight = round(profile.weight * KG_TO_LBS, 1)
        else:
            display_weight = profile.weight

        # height
        if profile.height_unit_preference == "ft_in" and profile.height is not None:
            cm = profile.height
            total_inches = cm * CM_TO_IN
            feet = int(total_inches // 12)
            inches = round(total_inches - (feet * 12), 1)

            display_height = None  # we will use feet/in separately
        else:
            display_height = profile.height
            feet = None
            inches = None

        user_form = UserUpdateForm(instance=request.user)
        form = ProfileUpdateForm(
            instance=profile,
            initial={
                "weight": display_weight,
                "height": display_height,
                "weight_unit_preference": profile.weight_unit_preference,
                "height_unit_preference": profile.height_unit_preference,
                "distance_unit_preference": profile.distance_unit_preference,
            }
        )

    return render(
        request,
        "accounts/profile_update.html",
        {
            "user_form": user_form,
            "profile_form": form,
            "height_feet": feet,
            "height_inches": inches,
        },
    )

@staff_member_required
def admin_dashboard(request):
    """
    Admin dashboard showing overall app statistics.
    Only accessible to staff/admin users.
    """
    # Time ranges for analysis
    now = timezone.now()
    last_30_days = now - timedelta(days=30)
    last_7_days = now - timedelta(days=7)
    
    # User Statistics
    total_users = User.objects.count()
    active_users_30d = User.objects.filter(
        workouts__created_at__gte=last_30_days
    ).distinct().count()
    active_users_7d = User.objects.filter(
        workouts__created_at__gte=last_7_days
    ).distinct().count()
    new_users_30d = User.objects.filter(
        date_joined__gte=last_30_days
    ).count()
    
    # Workout Statistics
    total_workouts = Workout.objects.count()
    workouts_30d = Workout.objects.filter(created_at__gte=last_30_days).count()
    workouts_7d = Workout.objects.filter(created_at__gte=last_7_days).count()
    
    # Average workout metrics
    avg_duration = Workout.objects.aggregate(Avg('duration'))['duration__avg'] or 0
    avg_calories = Workout.objects.aggregate(Avg('calories'))['calories__avg'] or 0
    avg_distance = Workout.objects.aggregate(Avg('distance'))['distance__avg'] or 0
    
    # Total metrics
    total_duration = Workout.objects.aggregate(Sum('duration'))['duration__sum'] or 0
    total_calories = Workout.objects.aggregate(Sum('calories'))['calories__sum'] or 0
    total_distance = Workout.objects.aggregate(Sum('distance'))['distance__sum'] or 0
    
    # Workout type distribution
    workout_types = Workout.objects.values('workout_type').annotate(
        count=Count('id'),
        total_duration=Sum('duration'),
        avg_duration=Avg('duration')
    ).order_by('-count')
    
    # Top users by workout count
    top_users = User.objects.annotate(
        workout_count=Count('workouts'),
        total_duration=Sum('workouts__duration'),
        total_distance=Sum('workouts__distance')
    ).filter(workout_count__gt=0).order_by('-workout_count')[:10]
    
    # Routes statistics
    total_routes = WorkoutRoute.objects.count()
    workouts_with_routes = Workout.objects.filter(route__isnull=False).count()
    
    # Most popular routes (by total points/complexity)
    top_routes = WorkoutRoute.objects.select_related('workout', 'workout__user').annotate(
        points_count=Count('id')
    ).order_by('-id')[:5]
    
    # Recent activity
    recent_workouts = Workout.objects.select_related('user').order_by('-created_at')[:10]
    
    context = {
        # User stats
        'total_users': total_users,
        'active_users_30d': active_users_30d,
        'active_users_7d': active_users_7d,
        'new_users_30d': new_users_30d,
        
        # Workout stats
        'total_workouts': total_workouts,
        'workouts_30d': workouts_30d,
        'workouts_7d': workouts_7d,
        
        # Averages
        'avg_duration': round(avg_duration, 1),
        'avg_calories': round(avg_calories, 0),
        'avg_distance': round(avg_distance, 2),
        
        # Totals
        'total_duration': total_duration,
        'total_duration_hours': round(total_duration / 60, 1),
        'total_calories': total_calories,
        'total_distance': round(total_distance, 2),
        
        # Distributions
        'workout_types': workout_types,
        'top_users': top_users,
        
        # Routes
        'total_routes': total_routes,
        'workouts_with_routes': workouts_with_routes,
        'top_routes': top_routes,
        
        # Recent activity
        'recent_workouts': recent_workouts,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)

def km_to_miles(km):
    return km * 0.621371

def miles_to_km(miles):
    return miles / 0.621371

def kg_to_lbs(kg):
    return kg * 2.20462

def lbs_to_kg(lbs):
    return lbs / 2.20462

def cm_to_inches(cm):
    return cm * 0.393701

def inches_to_cm(inches):
    return inches / 0.393701