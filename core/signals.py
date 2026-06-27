from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
import random

from .models import Profile


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        colors = ['#6366f1', '#ec4899', '#10b981', '#f59e0b', '#3b82f6', '#8b5cf6', '#06b6d4', '#f97316']
        Profile.objects.get_or_create(
            user=instance,
            defaults={'avatar_color': random.choice(colors)}
        )
