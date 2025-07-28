import time

from celery import shared_task
from video_app.models import Video
from video_app.utils import renew_temp_links
from django.core.paginator import Paginator


@shared_task
def update_links():
    """
    Fetch all videos from the database and renew their temporary links.
    """
    try:
        all_videos = Video.objects.all()
        paginator = Paginator(all_videos, 100)

        for page_number in paginator.page_range:
            page = paginator.page(page_number)
            renew_temp_links(page.object_list)

        print(f"Update done {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

    except Exception as e:

        print(f"Error updating links: {e}")

