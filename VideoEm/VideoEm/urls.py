
"""
URL configuration for VideoEm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from VideoEm import settings
from video_app.views import page_not_found, VideoAddAPIPost, VideoAPIGet, MyHistoryAPIGet, UserAPIGet, \
    VideoAPIPatch, HistoryAddAPIPost, SubscriptionAPI, GetInvoiceAPI, RegisterAPI, SearchAPI, TagsAPICreate, \
    TagsAPIGet, telegram_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('video_app.urls')),
    path('api/v1/video_add', VideoAddAPIPost.as_view(), name='video_add'),
    path('api/v1/video_get', VideoAPIGet.as_view(), name='video_get'),
    path('api/v1/watched_videos', MyHistoryAPIGet.as_view(), name='watched_videos_list'),
    path('api/v1/user_get/<int:telegram_id>', UserAPIGet.as_view(), name='user_get'),
    path('api/v1/update_video/<str:video_id>', VideoAPIPatch.as_view(), name='update_views'),
    path('api/v1/history_add', HistoryAddAPIPost.as_view(), name='history_add'),
    path('api/v1/subscriptions', SubscriptionAPI.as_view(), name='subscriptions'),
    path('api/v1/invoice_link', GetInvoiceAPI.as_view(), name='invoice_link'),
    path('api/v1/register_user', RegisterAPI.as_view(), name='register'),
    path('api/v1/search', SearchAPI.as_view(), name='search'),
    path('api/v1/create_tag', TagsAPICreate.as_view(), name='create_tag'),
    path('api/v1/get_tag', TagsAPIGet.as_view(), name='get_tag'),
    path('webhook/', telegram_webhook, name='telegram_webhook'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = page_not_found
