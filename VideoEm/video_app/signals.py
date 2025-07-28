from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from django.core.cache import cache
from .models import Video, TelegramUser, Subscription, Tag


@receiver(post_save, sender=Video)
@receiver(post_delete, sender=Video)
def update_user_stars_amount(sender, instance, **kwargs):
    """Update user stars amount when someone added it to one of user`s video"""
    user = instance.user
    user.stars_count = user.uploader.aggregate(Sum('stars'))['stars__sum'] or 0
    user.save()


@receiver(post_save, sender=Video)
@receiver(post_delete, sender=Video)
def clear_video_cache(sender, instance, **kwargs):
    """Clear cache when videos are updated or deleted"""
    keys = cache.keys('video_get:*')
    if keys:
        cache.delete_many(keys)


@receiver(post_save, sender=TelegramUser)
@receiver(post_delete, sender=TelegramUser)
def invalidate_user_cache_on_change(sender, instance, **kwargs):
    """Clear cache when user info are updated or deleted"""
    cache_key = f'user_api_get_{instance.telegram_id}'
    cache.delete(cache_key)


@receiver(post_save, sender=Subscription)
@receiver(post_delete, sender=Subscription)
def invalidate_subscription_cache_on_change(sender, instance, **kwargs):
    """Clear cache when subscription are updated or deleted"""
    cache_key = f'subscription_{instance.from_user.telegram_id}'
    cache.delete(cache_key)


@receiver(post_save, sender=Tag)
@receiver(post_delete, sender=Tag)
def invalidate_user_cache_on_change(sender, instance, **kwargs):
    """Clear cache when tags are added or deleted"""
    cache_key = 'tags_api_get'
    cache.delete(cache_key)

