import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

# 1. Profile Model
class Profile(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('developer', 'Developer'),
        ('app_inspector', 'App Inspector'),
        ('creator', 'Creator'),
        ('Official', 'Official'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    talk_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profiles/', default='default.png')
    bio = models.TextField(blank=True)
    friends = models.ManyToManyField(User, related_name='user_friends', blank=True)

    # --- Role & Verification ---
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_verified = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    # --- Chat Features ---
    is_typing = models.BooleanField(default=False)

    # --- Ban System Fields ---
    is_banned = models.BooleanField(default=False)
    ban_reason = models.CharField(max_length=255, blank=True, null=True)
    ban_until = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.role})"

    def is_online(self):
        if self.last_seen:
            return timezone.now() < self.last_seen + timedelta(minutes=5)
        return False

    def has_ban_expired(self):
        if self.is_banned and self.ban_until:
            return timezone.now() > self.ban_until
        return False

    def get_role_badge(self):
        if self.role == 'developer':
            return {'class': 'mark-developer', 'icon': 'bi-patch-check-fill', 'title': 'Developer'}
        elif self.role == 'app_inspector':
            return {'class': 'mark-inspector', 'icon': 'bi-check-circle-fill', 'title': 'App Inspector'}
        elif self.role == 'creator':
            return {'class': 'mark-creator', 'icon': 'bi-patch-check-fill', 'title': 'Creator'}
        elif self.role == 'Official':
            return {'class': 'mark-official', 'icon': 'bi-patch-check-fill', 'title': 'Official'}
        return None

# 2. Post Model
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='post_likes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.author.username}'s post - {self.id}"

    def total_likes(self):
        return self.likes.count()

# 3. Story Model
class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    image = models.ImageField(upload_to='stories/', blank=True, null=True)
    caption = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(hours=24)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Stories"

# 4. Comment Model
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.id}"

# 5. Friend Request Model
class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

# 6. Message Model
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    voice_note = models.FileField(upload_to='voice_notes/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender} to {self.receiver}"

# 7. Notification Model
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20)
    content = models.TextField(blank=True, null=True)
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

# 8. Block System Model
class BlockedUser(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')

# 9. Admin Broadcast Model
class AdminBroadcast(models.Model):
    subject = models.CharField(max_length=100, blank=True, null=True, default="Official Message")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Broadcast: {self.subject} ({self.created_at.date()})"

# --- SIGNALS ---

@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        # Bot အတွက် သီးသန့် ID သတ်မှတ်ခြင်း
        if instance.username == 'ThuTalkBot':
            new_talk_id = 'thutalk-01'
            role = 'Official'
        else:
            # ပုံမှန် User များအတွက် talk-XXXX format
            new_talk_id = f"talk-{str(instance.id).zfill(4)}"
            # အကယ်၍ ID ထပ်နေပါက (ဥပမာ User ကို ဖျက်ပြီး ပြန်ဆောက်တာမျိုး) UUID အတို သုံးမည်
            if Profile.objects.filter(talk_id=new_talk_id).exists():
                new_talk_id = f"talk-{uuid.uuid4().hex[:6]}"
            role = 'user'

        Profile.objects.get_or_create(
            user=instance,
            defaults={'talk_id': new_talk_id, 'role': role}
        )
    else:
        # Profile မရှိသေးရင် အသစ်ဆောက်၊ ရှိပြီးသားဆိုရင် update ပဲလုပ်မယ် (talk_id ကို မထိဘူး)
        if not hasattr(instance, 'profile'):
            new_talk_id = f"talk-{str(instance.id).zfill(4)}"
            if Profile.objects.filter(talk_id=new_talk_id).exists():
                new_talk_id = f"talk-{uuid.uuid4().hex[:6]}"
            Profile.objects.create(user=instance, talk_id=new_talk_id)
        else:
            instance.profile.save()

@receiver(post_save, sender=AdminBroadcast)
def send_broadcast_to_all_users(sender, instance, created, **kwargs):
    if created:
        try:
            # ThuTalkBot အမည်ဖြင့် User ကို ရှာမည် (မရှိရင် အလိုအလျောက် ဆောက်မည်)
            bot_user, _ = User.objects.get_or_create(username='ThuTalkBot')

            # Bot ကိုယ်တိုင်ကို ချန်လှပ်ပြီး ကျန်တဲ့ User အားလုံးကို ရှာမည်
            users = User.objects.exclude(id=bot_user.id)

            broadcast_list = [
                Message(
                    sender=bot_user,
                    receiver=user,
                    content=f"📢 {instance.subject}\n\n{instance.message}"
                ) for user in users
            ]
            if broadcast_list:
                Message.objects.bulk_create(broadcast_list)
        except Exception as e:
            # Error တက်ရင် site ရပ်မသွားအောင် print ပဲထုတ်ထားမယ်
            print(f"Broadcast system error: {e}")