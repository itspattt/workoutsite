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

    # Progress dashboard
    path('progress/', views.progress_dashboard, name='progress_dashboard'),

    # Data endpoint for charts
    path('progress/data/', views.progress_data, name='progress_data'),

    # Feed (Achievement Posts)
    path("feed/", views.feed_view, name="feed"),
    path("feed/new/<int:workout_id>/", views.create_feed_post, name="create_feed_post"),
    # Achievement editing
    path("feed/edit/<int:post_id>/", views.edit_feed_post, name="edit_feed_post"),
    path("feed/delete/<int:post_id>/", views.delete_feed_post, name="delete_feed_post"),

    # Public shared workout view
    path('shared/<int:pk>/', views.public_workout_detail, name='public_workout_detail'),
]