import uuid
import requests
from django.db import transaction

from django.db.models import OuterRef, Subquery
from django.http import HttpResponse, StreamingHttpResponse
from django.utils.text import slugify
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, \
    RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes, api_view
from rest_framework import status
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.views import APIView
from django.db.models import Count

from .forms import EditVideoForm
from .models import TelegramUser, Video, WatchingHistory, Subscription, Payment, SlugWord, Tag
from .serializers import VideoAddSerializer, UserSerializer, VideoGetSerializerBase, \
    WatchingHistorySerializer, SubscriptionSerializer, TagsSerializer, VideoGetSerializerWithSlugwords, \
    VideoGetSerializerWithTags
from .pagination import VideoCursorPagination, HistoryCursorPagination
from bot_main import BOT_TOKEN


class VideoAddAPIPost(CreateAPIView):
    """
    API endpoint to add a new video to the database.
    """
    queryset = Video.objects.all()
    serializer_class = VideoAddSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({'result': 'Success!'}, status=status.HTTP_201_CREATED)


class VideoAPIGet(ListAPIView):
    """
    API endpoint to retrieve videos.
    Supports filtering by user(s).
    """
    serializer_class = VideoGetSerializerBase
    pagination_class = VideoCursorPagination

    def get_queryset(self):
        """
        Get all videos or filter by user ID(s) if 'user(s)' query parameter is provided.
        Example request:
        /api/videos/ - all published videos
        /api/videos/?user=12345 - all videos uploaded by user with telegram_id=12345
        /api/videos/?user=12345,67890 - all published videos uploaded by users with telegram_id=12345 and telegram_id=67890
        """
        user_id = self.request.query_params.get('user')
        user_ids = self.request.query_params.get('users')

        if user_id:
            return Video.objects.filter(user=user_id)

        if user_ids:
            telegram_ids = user_ids.split(',')
            return Video.published.filter(user__in=telegram_ids)

        return Video.published.all().order_by('-time_created')

    def list(self, request, *args, **kwargs):
        """
        Handles pagination and response formatting.
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MyHistoryAPIGet(ListAPIView):
    """
    API endpoint to retrieve videos watched by a specific user, ordered by the most recent watch time.
    """
    serializer_class = VideoGetSerializerBase
    pagination_class = HistoryCursorPagination

    def get_queryset(self):
        telegram_id = self.request.query_params.get('user')

        if not telegram_id:
            return Response({"error": "The 'user' query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = TelegramUser.objects.get(telegram_id=telegram_id)

        if not user:
            return Video.objects.none()

        latest_watch_subquery = WatchingHistory.objects.filter(
            user=user, video_id=OuterRef('video_id')
        ).values('watched_at')

        history = Video.objects.filter(watchinghistory__user=user).annotate(
            watched_at=Subquery(latest_watch_subquery)).order_by('-watched_at')

        print(history)

        return history


class UserAPIGet(RetrieveAPIView):
    """
    API endpoint to retrieve details of a specific user.
    """
    serializer_class = UserSerializer
    queryset = TelegramUser.objects.all()
    lookup_field = 'telegram_id'


class VideoAPIPatch(RetrieveUpdateAPIView):
    """
    API endpoint to update details of a specific video.
    """
    queryset = Video.objects.all()
    serializer_class = VideoGetSerializerBase
    lookup_field = 'video_id'


class HistoryAddAPIPost(CreateAPIView):
    """
    API endpoint to add a new entry to the watching history.
    """
    queryset = WatchingHistory.objects.all()
    serializer_class = WatchingHistorySerializer


class SubscriptionAPI(APIView):

    def get(self, request, *args, **kwargs):
        """
        Retrieve all subscriptions for a user.
        Requires the 'telegram_id' query parameter.
        """
        telegram_id = request.query_params.get('telegram_id')

        if not telegram_id:
            return Response({'error': 'telegram_id query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        subscriptions = user.subscriptions_from.all()

        subscriptions_data = SubscriptionSerializer(subscriptions, many=True).data

        return Response({'subscriptions': subscriptions_data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Add a subscription.
        Requires 'from_user' and 'to_user' in the request body.
        """
        from_user_id = request.data.get('from_user')
        to_user_id = request.data.get('to_user')

        if not from_user_id or not to_user_id:
            return Response({'error': 'Both from_user and to_user are required'}, status=status.HTTP_400_BAD_REQUEST)

        if from_user_id == to_user_id:
            return Response({'error': 'Cannot subscribe to yourself'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from_user = TelegramUser.objects.get(telegram_id=from_user_id)
            to_user = TelegramUser.objects.get(telegram_id=to_user_id)
        except TelegramUser.DoesNotExist:
            return Response({'error': 'One or both users not found'}, status=status.HTTP_404_NOT_FOUND)

        if Subscription.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({'error': 'Subscription already exists'}, status=status.HTTP_400_BAD_REQUEST)

        subscription = Subscription(from_user=from_user, to_user=to_user)
        subscription.save()

        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        """
        Delete a subscription.
        Requires 'from_user' and 'to_user' in the request body.
        """
        from_user_id = request.data.get('from_user')
        to_user_id = request.data.get('to_user')

        if not from_user_id or not to_user_id:
            return Response({'error': 'Both from_user and to_user are required'}, status=status.HTTP_404_NOT_FOUND)

        try:
            subscription = Subscription.objects.get(from_user__telegram_id=from_user_id,
                                                    to_user__telegram_id=to_user_id)
        except Subscription.DoesNotExist:
            return Response({'error': 'Subscription not found'}, status=status.HTTP_404_NOT_FOUND)

        subscription.delete()
        return Response({'message': 'Subscription deleted successfully'}, status=status.HTTP_200_OK)


class GetInvoiceAPI(APIView):
    """
    API to obtain invoice url from telegram to continue payment
    The payment is for liking a video, with a cost of 1 Telegram star.
    """

    def get(self, request, *args, **kwargs):
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/createInvoiceLink'
        unique_id = uuid.uuid4()
        user = request.query_params.get('user')
        video_id = request.query_params.get('video')

        if not user or not video_id:
            return Response({'error': 'Both user and video query parameters are required'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user_obj = TelegramUser.objects.get(telegram_id=user)
            video_obj = Video.objects.get(video_id=video_id)
        except (TelegramUser.DoesNotExist, Video.DoesNotExist):
            return Response({'error': 'Invalid user or video ID'}, status=status.HTTP_404_NOT_FOUND)

        invoice_data = {'title': 'Like',
                        'description': 'Like Video',
                        'payload': f'{unique_id}&&&{video_id}',
                        'provider_token': '',
                        'currency': 'XTR',
                        'prices': [{'label': 'Like', 'amount': 1}]}

        try:
            response = requests.post(url, json=invoice_data)
            response_data = response.json()
            invoice_link = response_data.get('result')
            if invoice_link:
                Payment.objects.create(user_id=user, payment_id=unique_id)
                return Response({'invoice_link': invoice_link}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to generate invoice link', 'details': response_data},
                                status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException as e:
            return Response({'error': 'API request failed', 'details': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisterAPI(APIView):
    """
    API endpoint to register a new user or retrieve an existing user's data.
    Requires 'telegram_id' in the request data.
    """
    def post(self, request, *args, **kwargs):
        data = request.data
        telegram_id_value = data.get('telegram_id')

        if not telegram_id_value:
            return Response({'error': 'telegram_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id_value)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except TelegramUser.DoesNotExist:
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SearchAPI(APIView):
    """
    API endpoint to search videos by title.
    Requires the 'q' query parameter.
    """
    pagination_class = VideoCursorPagination

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        query_tags = request.query_params.get('tags', '')

        if query:
            query_slug = slugify(query)
            query_words = set(word for word in query_slug.split('-') if word)

            if not query_words:
                return Response([], status=status.HTTP_400_BAD_REQUEST)

            matched_words = SlugWord.objects.filter(word__in=query_words)

            videos = Video.objects.filter(slug_words__in=matched_words).distinct().prefetch_related('slug_words')
            videos = videos.annotate(match_count=Count('slug_words')).order_by('-match_count', '-time_published')

            paginator = VideoCursorPagination()
            paginated_videos = paginator.paginate_queryset(videos, request)

            serializer = VideoGetSerializerWithSlugwords(paginated_videos, many=True)

            return paginator.get_paginated_response(serializer.data)

        elif query_tags:

            tags_list = query_tags.split(',')

            videos = Video.objects.filter(tags__tag__in=tags_list).distinct().prefetch_related('tags')

            filtered_videos = [
                video for video in videos
                if set(video.tags.values_list('tag', flat=True)).issuperset(tags_list)
            ]

            video_ids = [video.id for video in filtered_videos]

            queryset = Video.objects.filter(id__in=video_ids)

            paginator = VideoCursorPagination()
            paginated_videos = paginator.paginate_queryset(queryset, request)

            serializer = VideoGetSerializerWithTags(paginated_videos, many=True)

            return paginator.get_paginated_response(serializer.data)

        else:
            return Response([], status=status.HTTP_400_BAD_REQUEST)


class TagsAPICreate(CreateAPIView):
    """
    API endpoint to create new tag.
    """
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer


class TagsAPIGet(ListAPIView):
    """
    API endpoint to retrieve tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer


def index(request):
    return render(request, 'video_app/index.html')


def main(request):
    return render(request, 'video_app/main.html', {"show_back_button": False})


def account(request):
    return render(request, 'video_app/account.html', {"show_back_button": True})


def page_not_found(request, exception):
    return render(request, 'video_app/404.html', {"show_back_button": True})


def subscriptions(request):
    return render(request, 'video_app/subscriptions.html', {"show_back_button": True})


def search(request):
    return render(request, 'video_app/search.html', {"show_back_button": True})


def tag_search(request):
    return render(request, 'video_app/tag_search.html', {"show_back_button": True})


def proxy_video(request):
    """
    Proxy for video links to handle cross-origin restrictions.
    Requires 'video_url' as a query parameter.
    """
    video_url = request.GET.get('video_url')

    if not video_url:
        return HttpResponse("Missing 'video_url' parameter", status=400)

    try:
        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        video_response = StreamingHttpResponse(
            response.iter_content(chunk_size=8192),
            content_type='video/mp4'
        )

        video_response['Content-Disposition'] = 'inline; filename="video.mp4"'
        video_response['Access-Control-Allow-Origin'] = '*'
        return video_response

    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Error fetching video: {str(e)}", status=500)


def edit_video(request, video_id):
    instance = get_object_or_404(Video.objects.prefetch_related('tags'), video_id=video_id)

    if request.method == 'POST':

        if "delete" in request.POST:
            instance.delete()
            return redirect('account')

        form = EditVideoForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('account')
    else:
        form = EditVideoForm(instance=instance)

    return render(request, 'video_app/edit_video.html', {'form': form, 'video': instance, "show_back_button": True})


def view_video(request, video_slug):
    instance = get_object_or_404(Video, video_slug=video_slug)

    tags = Tag.objects.filter(video=instance.pk)
    user = get_object_or_404(TelegramUser, pk=instance.user.pk)

    return render(request, 'video_app/view_video.html', {'video': instance, 'author': user, "show_back_button": True,
                                                         'tags': tags})


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def telegram_webhook(request):
    """
    Handle requests from telegram to server
    After using GetInvoiceAPI telegram send request (with pre_checkout_query parameter)
    to server and server must response to proceed payment confirmation.
    This request from telegram contain payload information which can be used to verify
    payment and make corresponding changes in DB.
    """
    update = request.data

    if 'pre_checkout_query' in update:
        try:
            pre_checkout_query_id = update['pre_checkout_query']['id']
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerPreCheckoutQuery"

            requests.post(url, data={"pre_checkout_query_id": pre_checkout_query_id, "ok": True})

            user_id = update['pre_checkout_query']['from']['id']
            invoice_payload = update['pre_checkout_query']['invoice_payload']
            parts = invoice_payload.split("&&&")

            video_id = parts[1]
            payment_id = uuid.UUID(parts[0])

            try:
                payment = Payment.objects.get(user=user_id, payment_id=payment_id)
            except Payment.DoesNotExist:
                return Response({"status": "fail", "error": "Payment record not found"})

            try:
                video = Video.objects.get(video_id=video_id)
            except Video.DoesNotExist:
                return Response({"status": "fail", "error": "Video not found"})

            if payment.status == "paid":
                return Response({"status": "fail", "error": "Payment already processed"})

            with transaction.atomic():
                video.stars += 1
                video.save()
                payment.status = "paid"
                payment.save()

            return Response({"status": "success"})

        except Exception as e:
            return Response({"status": "fail", "error": str(e)})
    else:
        return Response({"status": "ok"})
