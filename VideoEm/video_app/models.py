import uuid

from django.db import models


class PublishedManager(models.Manager):
    """ Manager for choosing video with is_published=True """
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)


class TelegramUser(models.Model):
    """ Table of users """
    telegram_id = models.PositiveBigIntegerField(unique=True)
    telegram_fullname = models.CharField(max_length=255)
    stars_count = models.PositiveIntegerField(default=0)
    time_create = models.DateTimeField(auto_now_add=True)
    subscriptions = models.ManyToManyField('self', through='Subscription', symmetrical=False,
                                           related_name='subscribers')

    objects = models.Manager()

    def __str__(self):
        return f"{self.telegram_fullname} ({self.telegram_id})"

    class Meta:
        ordering = ['-time_create']
        indexes = [models.Index(fields=['time_create', 'telegram_id']),
                   models.Index(models.F('time_create').desc(), name='time_create_desc')]


class Subscription(models.Model):
    """ Table of subscriptions """
    from_user = models.ForeignKey('TelegramUser', to_field='telegram_id', related_name='subscriptions_from', on_delete=models.CASCADE)
    to_user = models.ForeignKey('TelegramUser', to_field='telegram_id', related_name='subscriptions_to', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return f"{self.from_user} -> {self.to_user}"


class SlugWord(models.Model):
    """ Table of words which used for search based on video titles """
    word = models.CharField(max_length=50, db_index=True, unique=True)

    objects = models.Manager()

    def __str__(self):
        return self.word


class Tag(models.Model):
    """ Table of tags which used for search """
    tag = models.CharField(max_length=50, db_index=True, unique=True)

    objects = models.Manager()

    def __str__(self):
        return self.tag


class Video(models.Model):
    """ Table of videos """
    title = models.TextField(null=True)
    user = models.ForeignKey('TelegramUser', to_field='telegram_id', on_delete=models.PROTECT, related_name='uploader')
    video_id = models.CharField(max_length=255, unique=True)
    time_created = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    stars = models.PositiveIntegerField(default=0)
    temp_link = models.TextField(null=True)
    time_published = models.DateTimeField(null=True)
    video_slug = models.SlugField(default='', null=False)
    description = models.TextField(null=True)
    slug_words = models.ManyToManyField(SlugWord, related_name='videos', blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-time_published']
        indexes = [models.Index(fields=['time_published', 'stars', 'user_id', 'view_count', 'video_slug']),
                   models.Index(models.F('time_published').desc(), name='time_published_desc')]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.video_slug:
            words = set(self.video_slug.split('-'))
            word_objs = [SlugWord.objects.get_or_create(word=word)[0] for word in words]
            self.slug_words.set(word_objs)

    def __str__(self):
        return self.title or f"Video {self.video_id}"

class WatchingHistory(models.Model):
    """ Table for write user watching history """
    video = models.ForeignKey('Video', to_field='video_id', on_delete=models.PROTECT)
    user = models.ForeignKey('TelegramUser', to_field='telegram_id', on_delete=models.PROTECT)
    watched_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-watched_at']
        indexes = [models.Index(models.F('watched_at').desc(), name='watched_at_desc'),
                   models.Index(fields=['user', 'video'])]

    def __str__(self):
        return f"{self.user} watched {self.video} at {self.watched_at}"


class Payment(models.Model):
    """ Table for users payments """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]

    user = models.ForeignKey('TelegramUser', to_field='telegram_id', on_delete=models.PROTECT)
    payment_id = models.UUIDField(default=uuid.uuid4, editable=False)
    payment_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    objects = models.Manager()

    def __str__(self):
        return f"Payment {self.payment_id} by {self.user} is {self.status}"



