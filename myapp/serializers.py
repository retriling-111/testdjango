from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Post, Comment, Message, Story

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Profile
        fields = ['username', 'talk_id', 'bio', 'profile_pic', 'role']

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    author_pic = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author_name', 'author_pic', 'content', 'image', 'created_at', 'likes_count']

    def get_author_pic(self, obj):
        if obj.author.profile.profile_pic:
            return obj.author.profile.profile_pic.url
        return '/static/default_profile.png'

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.ReadOnlyField(source='sender.username')
    class Meta:
        model = Message
        fields = ['id', 'sender_name', 'content', 'timestamp', 'is_read', 'image', 'voice_note']

class StorySerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    user_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ['id', 'username', 'user_avatar', 'image', 'caption', 'created_at']

    def get_user_avatar(self, obj):
        if obj.user.profile.profile_pic:
            return obj.user.profile.profile_pic.url
        return '/static/default_profile.png'