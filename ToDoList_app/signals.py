from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task

@receiver(post_save, sender=Task)
def init_task(sender, instance, created, **kwargs):
    if created:
        if instance.is_done is None:
            instance.is_done = False
            instance.save()
        print(f"✅ Создана новая задача: {instance.title}")
