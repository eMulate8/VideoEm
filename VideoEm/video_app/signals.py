from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from .models import Video, TelegramUser


@receiver(post_save, sender=Video)
@receiver(post_delete, sender=Video)
def update_user_stars_count(sender, instance, **kwargs):
    user = instance.user
    user.stars_count = user.uploader.aggregate(Sum('stars'))['stars__sum'] or 0
    user.save()
