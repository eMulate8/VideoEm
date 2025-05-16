import requests
from django.db.models import QuerySet

from bot_main import BOT_TOKEN


def get_new_temp_link(video_id):
    """
    Fetch a new temporary link for a video from the Telegram API.
    Temporary link is valid for at least one hour.
    """
    get_link_url = f'https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={video_id}'

    try:
        response = requests.get(get_link_url)
        response.raise_for_status()

        if response.json().get('ok', False):
            file_path = response.json()['result'].get('file_path')
            if file_path:
                return f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}'
        return None

    except requests.exceptions.RequestException as e:
        return None


def renew_temp_links(video_queryset: QuerySet):
    """
    Get new temporary links for all videos in the provided QuerySet.
    """
    updated_objects = []
    if not video_queryset.exists():
        return video_queryset

    for obj in video_queryset:
        is_temp_link_invalid = True
        if obj.temp_link:
            try:
                response = requests.head(obj.temp_link)
                is_temp_link_invalid = False
            except requests.exceptions.RequestException:
                is_temp_link_invalid = True

        if is_temp_link_invalid or (not is_temp_link_invalid and response.status_code == 404):

            temp_link = get_new_temp_link(obj.video_id)

            if temp_link:
                obj.temp_link = temp_link
                updated_objects.append(obj)

    if updated_objects:
        video_queryset.model.objects.bulk_update(updated_objects, ['temp_link'])

    return video_queryset
