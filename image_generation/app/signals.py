import os
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_log_folder(sender, instance, created, **kwargs):
    if created:
        user_folder = os.path.join('logs', instance.username)
        os.makedirs(user_folder, exist_ok=True)
