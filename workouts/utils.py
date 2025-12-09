from .models import Milestone, UserMilestone, Workout
from django.db.models import Sum, Count

def check_milestones(user):
    milestones = Milestone.objects.all()

    total_workouts = Workout.objects.filter(user=user).count()
    total_distance = Workout.objects.filter(user=user).aggregate(Sum('distance'))['distance__sum'] or 0
    total_duration = Workout.objects.filter(user=user).aggregate(Sum('duration'))['duration__sum'] or 0

    for m in milestones:
        if UserMilestone.objects.filter(user=user, milestone=m).exists():
            continue

        if m.milestone_type == "count" and total_workouts >= m.threshold:
            UserMilestone.objects.create(user=user, milestone=m, seen=False)

        elif m.milestone_type == "distance" and total_distance >= m.threshold:
            UserMilestone.objects.create(user=user, milestone=m, seen=False)

        elif m.milestone_type == "duration" and total_duration >= m.threshold:
            UserMilestone.objects.create(user=user, milestone=m, seen=False)

def new_milestone_count(request):
    if request.user.is_authenticated:
        count = UserMilestone.objects.filter(user=request.user, seen=False).count()
    else:
        count = 0
    return {'new_milestone_count': count}