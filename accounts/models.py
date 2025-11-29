# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    WEIGHT_UNITS = [
        ('kg', 'Kilograms (kg)'),
        ('lbs', 'Pounds (lbs)'),
    ]

    HEIGHT_UNITS = [
        ('cm', 'Centimeters (cm)'),
        ('ft_in', 'Feet/Inches'),
    ]

    DISTANCE_UNITS = [
        ('km', 'Kilometers (km)'),
        ('miles', 'Miles'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)  # stored in KG
    height = models.FloatField(null=True, blank=True)  # stored in CM

    weight_unit_preference = models.CharField(
        max_length=10, choices=WEIGHT_UNITS, default='kg'
    )
    height_unit_preference = models.CharField(
        max_length=10, choices=HEIGHT_UNITS, default='cm'
    )
    distance_unit_preference = models.CharField(
        max_length=10, choices=DISTANCE_UNITS, default='km'
    )

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()