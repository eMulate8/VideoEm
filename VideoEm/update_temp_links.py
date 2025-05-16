import os
import django
import schedule
import time
from django.core.paginator import Paginator


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VideoEm.settings')
django.setup()

from video_app.models import Video
from video_app.utils import renew_temp_links


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

if __name__ == "__main__":

    update_links()

    schedule.every().hour.do(update_links)
    try:
        while True:
            schedule.run_pending()
            time.sleep(10)
    except KeyboardInterrupt:
        print("Script stopped by user.")



