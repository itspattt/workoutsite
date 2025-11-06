from django.test import TestCase
from django.contrib.auth.models import User
from .models import Workout, WorkoutRoute


class WorkoutModelTest(TestCase):
    """
    Tests for the Workout model.
    Team can extend this with more comprehensive tests.
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_workout_creation(self):
        """Test that a workout can be created successfully"""
        workout = Workout.objects.create(
            user=self.user,
            workout_type='running',
            title='Morning Run',
            duration=30,
            distance=5.0,
            calories=300
        )
        
        self.assertEqual(workout.title, 'Morning Run')
        self.assertEqual(workout.duration, 30)
        self.assertEqual(str(workout.distance), '5.00')
    
    def test_workout_without_optional_fields(self):
        """Test that workouts can be created without distance and calories"""
        workout = Workout.objects.create(
            user=self.user,
            workout_type='yoga',
            title='Evening Yoga',
            duration=45
        )
        
        self.assertEqual(workout.title, 'Evening Yoga')
        self.assertIsNone(workout.distance)
        self.assertIsNone(workout.calories)


class WorkoutRouteModelTest(TestCase):
    """
    Tests for the WorkoutRoute model.
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.workout = Workout.objects.create(
            user=self.user,
            workout_type='running',
            title='Test Run',
            duration=30
        )
    
    def test_route_creation(self):
        """Test that a route can be created for a workout"""
        route_data = [[37.7749, -122.4194], [37.7750, -122.4195]]
        route = WorkoutRoute.objects.create(
            workout=self.workout,
            route_data=route_data
        )
        
        self.assertEqual(route.workout, self.workout)
        self.assertEqual(route.total_points, 2)
        self.assertEqual(route.route_data, route_data)


# Add more tests here for views, forms, etc.

