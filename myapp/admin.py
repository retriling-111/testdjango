from django.contrib import admin
from django.contrib.auth.models import User
from .models import (
    Profile, Post, Story, Comment,
    FriendRequest, Message, Notification,
    BlockedUser, AdminBroadcast
)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'talk_id', 'role', 'is_verified', 'is_banned']
    search_fields = ['user__username', 'talk_id']
    list_filter = ['role', 'is_verified', 'is_banned']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'content_snippet', 'created_at']
    search_fields = ['author__username', 'content']
    list_filter = ['created_at']

    def content_snippet(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_snippet.short_description = 'Content'

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'caption', 'created_at']
    list_filter = ['created_at']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at', 'parent']
    list_filter = ['created_at']
    search_fields = ['content', 'user__username']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'is_read', 'timestamp']
    list_filter = ['is_read', 'timestamp']
    search_fields = ['sender__username', 'receiver__username', 'content']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'sender', 'notification_type', 'is_seen', 'created_at']
    list_filter = ['notification_type', 'is_seen', 'created_at']

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'created_at']

@admin.register(BlockedUser)
class BlockedUserAdmin(admin.ModelAdmin):
    list_display = ['blocker', 'blocked', 'created_at']

# --- TALK OFFICIAL BOT BROADCAST SYSTEM ---

@admin.register(AdminBroadcast)
class AdminBroadcastAdmin(admin.ModelAdmin):
    """
    Admin က AdminBroadcast တင်လိုက်ရင် TalkOfficialBot အနေနဲ့
    User အားလုံးဆီ Message ရောက်သွားပါမယ်။
    """
    list_display = ['subject', 'created_at']
    search_fields = ['subject', 'message']

    def save_model(self, request, obj, form, change):
        # ၁။ စာကို Database ထဲ အရင် သိမ်းသည်
        super().save_model(request, obj, form, change)

        # ၂။ အသစ်ပို့တဲ့ Broadcast ဆိုလျှင် (Edit လုပ်တာမဟုတ်လျှင်)
        if not change:
            # Views နှင့် Models ထဲက Bot username 'TalkOfficialBot' နှင့် ညီအောင် ပြင်ပေးထားပါသည်
            bot_username = 'TalkOfficialBot'

            bot_user, created = User.objects.get_or_create(
                username=bot_username,
                defaults={
                    'is_active': True,
                    'is_staff': False,
                    'first_name': 'ThuTalk Official',
                    'last_name': 'Bot'
                }
            )

            # Bot ရဲ့ Profile ကို Update လုပ်သည်
            bot_profile, _ = Profile.objects.get_or_create(user=bot_user)
            bot_profile.role = 'Official'
            bot_profile.is_verified = True

            # Bot အတွက် Talk ID ကို talk-0000 ဟု သတ်မှတ်သည်
            if not bot_profile.talk_id:
                bot_profile.talk_id = "talk-0000"

            bot_profile.save()

            # ၃။ User အားလုံးဆီ Message ပို့မည်
            # Bot ကိုယ်တိုင်နှင့် အခြား AI Bot (ThuTalk) ကို ချန်လှပ်သည်
            all_users = User.objects.exclude(id=bot_user.id).exclude(username='ThuTalk')

            broadcast_messages = [
                Message(
                    sender=bot_user,
                    receiver=user,
                    content=f"📢 *{obj.subject}*\n\n{obj.message}"
                ) for user in all_users
            ]

            # Bulk create ဖြင့် Message များ တစ်ခါတည်းသွင်းသည်
            if broadcast_messages:
                Message.objects.bulk_create(broadcast_messages)

            # ၄။ Notification ပါ ပြရန်
            notifications = [
                Notification(
                    recipient=user,
                    sender=bot_user,
                    notification_type='message',
                    content=f"Official News: {obj.subject}"
                ) for user in all_users
            ]
            if notifications:
                Notification.objects.bulk_create(notifications)