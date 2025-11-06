from django.urls import path
from . import views

urlpatterns = [
    # Workout CRUD
    path('', views.workout_list, name='workout_list'),
    path('workout/<int:pk>/', views.workout_detail, name='workout_detail'),
    path('workout/new/', views.workout_create, name='workout_create'),
    path('workout/<int:pk>/edit/', views.workout_edit, name='workout_edit'),
    path('workout/<int:pk>/delete/', views.workout_delete, name='workout_delete'),
    
    # Route management
    path('workout/<int:pk>/route/', views.workout_add_route, name='workout_add_route'),
    path('workout/<int:pk>/route/delete/', views.workout_route_delete, name='workout_route_delete'),
]

