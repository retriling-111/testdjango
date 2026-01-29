from .models import Notification, FriendRequest, Message

def notification_count(request):
    if request.user.is_authenticated:
        # 1. တခြား Notifications များ (Like, Comment, FriendAccept စသည်)
        # Message အမျိုးအစား Noti တွေကို နှုတ်ထားချင်ရင် .exclude(notification_type='Message') သုံးနိုင်ပါတယ်
        general_noti = Notification.objects.filter(
            recipient=request.user,
            is_seen=False
        ).exclude(notification_type='Message').count()

        # 2. Friend Requests (အပ်ထားတာ မလက်ခံရသေးသမျှ count တက်နေမည်)
        friend_reqs = FriendRequest.objects.filter(to_user=request.user).count()

        # 3. Unread Messages (စကားပြောခန်းထဲမှာ မဖတ်ရသေးသော စာများ)
        # ဒါက base.html ရဲ့ chat icon မှာ ပြဖို့ပါ
        unread_messages = Message.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()

        return {
            'unread_notifications': general_noti + friend_reqs, # Bell icon အတွက်
            'unread_chats': unread_messages                  # Chat icon အတွက်
        }

    return {
        'unread_notifications': 0,
        'unread_chats': 0
    }