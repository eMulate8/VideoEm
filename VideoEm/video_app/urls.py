from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('main/', views.main, name='main'),
    path('account/', views.account, name='account'),
    path('proxy-video/', views.proxy_video, name='proxy_video'),
    path('edit_video/<str:video_id>/', views.edit_video, name='edit_video'),
    path('view_video/<slug:video_slug>/', views.view_video, name='view_video'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('search/', views.search, name='search'),
    path('tag_search/', views.tag_search, name='tag_search'),
]
