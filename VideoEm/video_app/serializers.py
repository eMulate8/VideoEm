from rest_framework import serializers

from .models import Video, TelegramUser, WatchingHistory, Subscription, Tag
from .utils import get_new_temp_link


class VideoAddSerializer(serializers.ModelSerializer):
    """
    Serializer for adding a new video.
    Handles user_id as a write-only field and fetches a temporary link for the video.
    """
    user_id = serializers.IntegerField(write_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Video
        fields = ['user_id', 'video_id', 'user']

    def create(self, validated_data):
        telegram_id = validated_data.pop('user_id')

        try:
            temp_link = get_new_temp_link(validated_data["video_id"])

            if temp_link:
                validated_data['temp_link'] = temp_link

        except Exception as e:
            raise serializers.ValidationError({"video_id": f"Failed to generate temporary link: {str(e)}"})

        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            raise serializers.ValidationError({"user_id": "User with the given telegram_id does not exist."})

        video = Video.objects.create(user=user, **validated_data)

        return video


class VideoGetSerializerBase(serializers.ModelSerializer):
    """
    Base serializer for retrieving video details.
    Includes username as read-only fields.
    """
    username = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['title', 'user', 'video_id', 'time_created', 'is_published', 'view_count', 'stars',
                  'temp_link', 'time_published', 'video_slug', 'description', 'tags', 'username', 'slug_words']

    def get_username(self, instance):
        return instance.user.telegram_fullname


class VideoGetSerializerWithSlugwords(VideoGetSerializerBase):
    """
    Serializer for retrieving video details.
    Includes slug words as read-only fields.
    Using for casual search.
    """
    slug_words = serializers.SerializerMethodField()

    def get_slug_words(self, instance):
        return [slug_word.word for slug_word in instance.slug_words.all()]


class VideoGetSerializerWithTags(VideoGetSerializerBase):
    """
    Serializer for retrieving video details.
    Includes tags as read-only fields.
    Using for tag search.
    """
    tags = serializers.SerializerMethodField()

    def get_tags(self, instance):
        return [tag.tag for tag in instance.tags.all()]


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving user details.
    Includes video count as a read-only field.
    """
    video_count = serializers.SerializerMethodField()

    class Meta:
        model = TelegramUser
        fields = ['id', 'telegram_id', 'telegram_fullname', 'stars_count', 'time_create', 'subscriptions',
                  'video_count']

    def get_video_count(self, instance):
        return instance.uploader.count()


class WatchingHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving watching history details.
    """
    class Meta:
        model = WatchingHistory
        fields = ['video', 'user']


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving subscription details.
    """
    class Meta:
        model = Subscription
        fields = ['from_user', 'to_user']


class TagsSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving tags.
    """
    class Meta:
        model = Tag
        fields = ['tag']
