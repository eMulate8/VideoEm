import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VideoEm.settings')
app = Celery('VideoEm')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['video_app'])
