import json
import random
import uuid
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Q, Max, Count
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime

from .models import Profile, Post, Comment, Message, Notification, FriendRequest, Story, BlockedUser, AdminBroadcast
from .forms import RegisterForm, PostForm, CommentForm, ProfileUpdateForm, UserUpdateForm

# --- BOT SETUP & LOGIC ---

def setup_bots():
    """
    ThuTalkBot (Official Bot) တစ်ကောင်တည်းကိုပဲ Setup လုပ်ပေးပါမယ်။
    """
    bot, created = User.objects.get_or_create(username='ThuTalkBot')
    profile, _ = Profile.objects.get_or_create(user=bot)

    # Bot ရဲ့ Talk ID နဲ့ Role ကို သတ်မှတ်ပေးခြင်း (မရှိသေးရင်)
    if not profile.talk_id or profile.talk_id != 'thutalk-01':
        profile.talk_id = 'thutalk-01'
        profile.role = 'Official'
        profile.bio = "ThuTalk Official Broadcast Bot & Assistant 📢🤖"
        profile.save()

def bot_auto_reply(user):
    """ User အသစ် Register လုပ်လျှင် ThuTalkBot မှ နှုတ်ဆက်စာပို့ရန် """
    setup_bots()
    try:
        chat_bot = User.objects.get(username='ThuTalkBot')
        welcome_msg = f"Hello {user.username}! ✨ ThuTalk ကနေ နွေးထွေးစွာ ကြိုဆိုပါတယ်။ ကျွန်တော်ကတော့ သင်တစ်ယောက်တည်း မဟုတ်အောင် အမြဲရှိနေပေးမယ့် အဖော်မွန်ပါ။ စကားတွေ အများကြီး ပြောကြရအောင်နော်!"
        if not Message.objects.filter(sender=chat_bot, receiver=user).exists():
            Message.objects.create(sender=chat_bot, receiver=user, content=welcome_msg)
    except User.DoesNotExist:
        pass

def get_bot_response(user_content):
    """ Keyword based logic for ThuTalkBot """
    content = user_content.lower()
    responses = {
        "ပင်ပန်း": ["ဒီနေ့အတွက် တကယ်တော်ခဲ့ပါတယ်နော်။ ❤️", "ပင်ပန်းနေပြီလား? ခဏလောက် နားလိုက်ပါဦး။"],
        "နေမကောင်း": ["ဟာ... ဂရုစိုက်ပါဦး။ ဆေးသောက်ပြီးပြီလား? 💊", "အားရှိအောင် စားပြီး အိပ်ရေးဝဝအိပ်နော်။"],
        "ဝမ်းနည်း": ["ဘာတွေဖြစ်လို့လဲ? စိတ်မကောင်းမဖြစ်ပါနဲ့နော်။ ကျွန်တော် ဒီမှာ ရှိနေပေးပါတယ်။ 🫂"],
        "မင်္ဂလာပါ": ["မင်္ဂလာပါဗျာ! ဒီနေ့လေးက သင့်အတွက် ပျော်စရာတွေပဲ ယူဆောင်လာပါစေ။ ✨", "Hi! စကားလာပြောတာ ဝမ်းသာပါတယ်ခင်ဗျ။"],
        "ကျေးဇူး": ["မလိုပါဘူးဗျာ၊ ကူညီပေးနိုင်တာ ကျွန်တော့်အတွက် ဝမ်းသာစရာပါ။ 😊"],
        "အိပ်တော့": ["ဟုတ်ကဲ့ပါ... မင်းလည်း စောစောအိပ်နော်။ အိပ်မက်လှလှမက်ပါစေ။ ✨", "Good night ပါဗျာ။ 🌙"],
        "နေကောင်းလား": ["ကျွန်တော် နေကောင်းပါတယ်ဗျာ။ မေးပေးလို့ ကျေးဇူးအများကြီးတင်ပါတယ်။ ❤️"]
    }
    for key, value in responses.items():
        if key in content:
            return random.choice(value)
    return "နားထောင်ပေးနေပါတယ်ဗျာ။ စိတ်ထဲရှိတာတွေ အကုန်ပြောပြလို့ရတယ်။ ✨"

# --- AUTHENTICATION ---

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            bot_auto_reply(user)
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            profile, _ = Profile.objects.get_or_create(user=user)
            if profile.is_banned:
                if profile.has_ban_expired():
                    profile.is_banned = False
                    profile.ban_until = None
                    profile.save()
                else:
                    time_left = profile.ban_until.strftime("%B %d, %Y at %I:%M %p")
                    messages.error(request, f"Your account is banned until {time_left}. Reason: {profile.ban_reason}")
                    return render(request, 'login.html', {'form': form})
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

# --- CORE (HOME & FEED) ---

@login_required(login_url='login')
def home(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.last_seen = timezone.now()
    profile.save(update_fields=['last_seen'])

    if profile.is_banned and not profile.has_ban_expired():
        logout(request)
        return redirect('login')

    blocked_ids = BlockedUser.objects.filter(blocker=request.user).values_list('blocked', flat=True)
    blocking_me = BlockedUser.objects.filter(blocked=request.user).values_list('blocker', flat=True)
    all_blocked_ids = list(blocked_ids) + list(blocking_me)

    time_threshold = timezone.now() - timedelta(hours=24)
    stories = Story.objects.filter(
        created_at__gte=time_threshold
    ).exclude(user_id__in=all_blocked_ids).select_related('user', 'user__profile').order_by('-created_at')

    stories_data = []
    for s in stories:
        stories_data.append({
            'id': s.id,
            'image': s.image.url if s.image else '',
            'caption': s.caption or '',
            'username': s.user.username,
            'is_mine': s.user == request.user,
            'role': s.user.profile.role,
            'user_avatar': s.user.profile.profile_pic.url if s.user.profile.profile_pic else '/static/default_profile.png',
            'created_at': str(naturaltime(s.created_at))
        })

    posts = Post.objects.exclude(
        author_id__in=all_blocked_ids
    ).select_related('author', 'author__profile').prefetch_related('likes', 'comments', 'comments__user').order_by('-created_at')

    return render(request, 'home.html', {
        'posts': posts,
        'stories': stories,
        'stories_json': json.dumps(stories_data),
        'user_profile': profile
    })

# --- POSTS & COMMENTS ---

@login_required
def add_post(request):
    if request.method == "POST":
        content = request.POST.get('content')
        image = request.FILES.get('image')
        if not content and not image:
            messages.error(request, "Cannot create empty post.")
            return redirect('home')
        Post.objects.create(author=request.user, content=content, image=image)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        messages.success(request, "Post added successfully!")
    return redirect('home')

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized.")
        return redirect('home')
    if request.method == "POST":
        post.content = request.POST.get('content', post.content)
        if request.FILES.get('image'):
            post.image = request.FILES.get('image')
        post.save()
        messages.success(request, "Post updated!")
        return redirect('home')
    return render(request, 'edit_post.html', {'post': post})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author == request.user or request.user.is_staff:
        post.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        messages.success(request, "Post deleted.")
    return redirect('home')

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        if content:
            parent_obj = Comment.objects.filter(id=parent_id).first() if parent_id else None
            comment = Comment.objects.create(post=post, user=request.user, content=content, parent=parent_obj)

            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author, sender=request.user,
                    notification_type='Comment', content=f"{request.user.username} commented on your post."
                )

            return JsonResponse({
                'status': 'success', 'username': request.user.username,
                'content': str(content), 'comment_id': comment.id,
                'profile_pic': request.user.profile.profile_pic.url if request.user.profile.profile_pic else '/static/default_profile.png',
                'comment_count': post.comments.count(),
                'parent_id': parent_id
            })
    return JsonResponse({'status': 'error'})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post = comment.post
    if comment.user == request.user or post.author == request.user or request.user.is_staff:
        comment.delete()
        return JsonResponse({'status': 'success', 'comment_count': post.comments.count()})
    return JsonResponse({'status': 'error'}, status=403)

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author, sender=request.user,
                notification_type='Like', content=f"{request.user.username} liked your post."
            )
    return JsonResponse({'liked': liked, 'like_count': post.likes.count()})

# --- CHAT SYSTEM ---

@login_required
def chat_list(request):
    blocked_ids = BlockedUser.objects.filter(blocker=request.user).values_list('blocked', flat=True)
    blocking_me = BlockedUser.objects.filter(blocked=request.user).values_list('blocker', flat=True)
    all_blocked = list(blocked_ids) + list(blocking_me)

    users = User.objects.filter(
        Q(sent_messages__receiver=request.user) | Q(received_messages__sender=request.user)
    ).distinct().exclude(id=request.user.id).exclude(id__in=all_blocked)

    chat_data = []
    for user in users:
        Profile.objects.get_or_create(user=user)
        last_msg = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) | (Q(sender=user) & Q(receiver=request.user))
        ).order_by('-timestamp').first()
        unread = Message.objects.filter(sender=user, receiver=request.user, is_read=False).count()
        chat_data.append({
            'user': user, 'last_message': last_msg,
            'unread_count': unread, 'role': user.profile.role
        })

    chat_data.sort(key=lambda x: x['last_message'].timestamp if x['last_message'] else timezone.now(), reverse=True)
    return render(request, 'chat_list.html', {'chat_data': chat_data})

@login_required
def chat_room(request, username):
    receiver = get_object_or_404(User, username=username)
    Profile.objects.get_or_create(user=receiver)

    Message.objects.filter(sender=receiver, receiver=request.user, is_read=False).update(is_read=True)

    is_blocked = BlockedUser.objects.filter(blocker=request.user, blocked=receiver).exists()
    am_i_blocked = BlockedUser.objects.filter(blocker=receiver, blocked=request.user).exists()

    return render(request, 'chat.html', {
        'receiver': receiver,
        'is_blocked': is_blocked,
        'am_i_blocked': am_i_blocked
    })

@login_required
def chat_profile_view(request, username):
    viewed_user = get_object_or_404(User, username=username)
    Profile.objects.get_or_create(user=viewed_user)
    return render(request, 'chat_profile.html', {'viewed_user': viewed_user})

@login_required
def search_messages(request, username):
    receiver = get_object_or_404(User, username=username)
    query = request.GET.get('q', '')
    messages_query = Message.objects.filter(
        (Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user)),
        content__icontains=query
    ).order_by('-timestamp')

    results = []
    for m in messages_query:
        results.append({
            'content': str(m.content),
            'sender': m.sender.username,
            'timestamp': m.timestamp.strftime('%I:%M %p')
        })
    return JsonResponse({'results': results})

@login_required
def send_message(request, username):
    receiver = get_object_or_404(User, username=username)

    if BlockedUser.objects.filter(Q(blocker=request.user, blocked=receiver) | Q(blocker=receiver, blocked=request.user)).exists():
        return JsonResponse({'status': 'error', 'message': 'Messaging blocked.'}, status=403)

    if request.method == "POST":
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')
        voice_note = request.FILES.get('voice_note')
        parent_id = request.POST.get('parent_id')
        parent_msg = Message.objects.filter(id=parent_id).first() if parent_id else None

        if content or image or voice_note:
            message = Message.objects.create(
                sender=request.user, receiver=receiver,
                content=content, image=image, voice_note=voice_note,
                parent=parent_msg
            )

            # Bot Reply Logic
            if receiver.username == 'ThuTalkBot':
                bot_reply_content = get_bot_response(content)
                Message.objects.create(sender=receiver, receiver=request.user, content=bot_reply_content)

            return JsonResponse({
                'status': 'success', 'id': message.id, 'content': str(message.content),
                'sender': request.user.username, 'timestamp': message.timestamp.strftime('%I:%M %p')
            })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_messages(request, username):
    receiver = get_object_or_404(User, username=username)
    messages_query = Message.objects.filter(
        (Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user))
    ).order_by('timestamp').select_related('sender', 'parent')

    Message.objects.filter(sender=receiver, receiver=request.user, is_read=False).update(is_read=True)

    msg_list = []
    for m in messages_query:
        msg_list.append({
            'id': m.id, 'sender': m.sender.username, 'content': str(m.content),
            'image': m.image.url if m.image else None,
            'voice_note': m.voice_note.url if m.voice_note else None,
            'timestamp': m.timestamp.strftime('%I:%M %p'), 'is_read': m.is_read,
            'parent_content': str(m.parent.content) if m.parent else None
        })
    return JsonResponse({
        'messages': msg_list,
        'me': request.user.username,
        'is_online': receiver.profile.is_online()
    })

@login_required
def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    if request.method == "POST":
        new_content = request.POST.get('content', '').strip()
        if new_content:
            message.content = new_content
            message.save()
            return JsonResponse({'status': 'success', 'new_content': str(new_content)})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.sender == request.user or message.receiver == request.user:
        message.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=403)

# --- PROFILE & SOCIAL ---

@login_required
def profile_view(request, username):
    viewed_user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=viewed_user)
    posts = Post.objects.filter(author=viewed_user).select_related('author', 'author__profile').order_by('-created_at')

    is_friend = request.user.profile.friends.filter(id=viewed_user.id).exists()
    sent_request = FriendRequest.objects.filter(from_user=request.user, to_user=viewed_user).exists()
    received_request = FriendRequest.objects.filter(from_user=viewed_user, to_user=request.user).exists()
    is_blocked = BlockedUser.objects.filter(blocker=request.user, blocked=viewed_user).exists()
    is_bot = (viewed_user.username == 'ThuTalkBot' or profile.role == 'Official')

    return render(request, 'profile.html', {
        'viewed_user': viewed_user, 'user_profile': profile,
        'user_posts': posts, 'is_friend': is_friend,
        'sent_request': sent_request, 'received_request': received_request,
        'is_blocked': is_blocked, 'is_bot': is_bot
    })

@login_required
def search_page(request):
    query = request.GET.get('q', '').strip()
    users_data = []
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(profile__talk_id__icontains=query) |
            Q(profile__bio__icontains=query)
        ).exclude(id=request.user.id).select_related('profile')

        for u in users:
            users_data.append({
                'user': u,
                'is_friend': request.user.profile.friends.filter(id=u.id).exists(),
                'sent_request': FriendRequest.objects.filter(from_user=request.user, to_user=u).exists(),
                'received_request': FriendRequest.objects.filter(from_user=u, to_user=request.user).exists(),
                'is_blocked': BlockedUser.objects.filter(blocker=request.user, blocked=u).exists(),
                'is_bot': (u.username == 'ThuTalkBot' or u.profile.role == 'Official'),
                'role': u.profile.role
            })
    return render(request, 'search.html', {'users_data': users_data, 'query': query})

@login_required
def all_friends_view(request, username):
    user = get_object_or_404(User, username=username)
    Profile.objects.get_or_create(user=user)
    return render(request, 'all_friends.html', {
        'viewed_user': user,
        'friends': user.profile.friends.all().select_related('profile')
    })

# --- FRIEND ACTIONS ---

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if to_user != request.user:
        FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def cancel_friend_request(request, user_id):
    FriendRequest.objects.filter(from_user=request.user, to_user_id=user_id).delete()
    return JsonResponse({'status': 'success'})

@login_required
def accept_friend(request, request_id):
    f_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    request.user.profile.friends.add(f_request.from_user)
    f_request.from_user.profile.friends.add(request.user)

    Notification.objects.create(
        recipient=f_request.from_user, sender=request.user,
        notification_type='FriendRequest', content=f"{request.user.username} accepted your friend request."
    )
    f_request.delete()
    return redirect('notifications')

@login_required
def delete_request(request, request_id):
    get_object_or_404(FriendRequest, id=request_id, to_user=request.user).delete()
    return redirect('notifications')

@login_required
def unfriend_user(request, user_id):
    target = get_object_or_404(User, id=user_id)
    request.user.profile.friends.remove(target)
    target.profile.friends.remove(request.user)
    return JsonResponse({'status': 'success'})

@login_required
def block_user(request, user_id):
    target = get_object_or_404(User, id=user_id)
    BlockedUser.objects.get_or_create(blocker=request.user, blocked=target)

    request.user.profile.friends.remove(target)
    target.profile.friends.remove(request.user)
    FriendRequest.objects.filter(Q(from_user=request.user, to_user=target) | Q(from_user=target, to_user=request.user)).delete()

    return JsonResponse({'status': 'success'})

@login_required
def unblock_user(request, user_id):
    target = get_object_or_404(User, id=user_id)
    BlockedUser.objects.filter(blocker=request.user, blocked=target).delete()
    return JsonResponse({'status': 'success'})

# --- SETTINGS & UPDATE ---

@login_required
def settings_view(request):
    blocked_list = BlockedUser.objects.filter(blocker=request.user).select_related('blocked', 'blocked__profile')
    return render(request, 'settings.html', {'blocked_list': blocked_list})

@login_required
def update_profile_ajax(request):
    if request.method == 'POST':
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        profile.bio = request.POST.get('bio', profile.bio)

        new_talk_id = request.POST.get('talk_id', profile.talk_id)

        if request.FILES.get('profile_pic'):
            profile.profile_pic = request.FILES.get('profile_pic')

        try:
            if new_talk_id and new_talk_id != profile.talk_id:
                if Profile.objects.filter(talk_id=new_talk_id).exclude(user=user).exists():
                    messages.error(request, "Talk ID already taken.")
                    return redirect('profile_view', username=user.username)
                profile.talk_id = new_talk_id

            user.save()
            profile.save()
            messages.success(request, "Profile updated!")
        except Exception:
            messages.error(request, "Update failed. Username might already be taken.")

        return redirect('profile_view', username=user.username)
    return redirect('settings')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated!')
            return redirect('settings')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        logout(request)
        messages.success(request, "Account deleted.")
        return redirect('login')
    return render(request, 'delete_account.html')

# --- NOTIFICATIONS & STORIES ---

@login_required
def notifications(request):
    f_requests = FriendRequest.objects.filter(to_user=request.user).select_related('from_user', 'from_user__profile')
    general_notifs = Notification.objects.filter(recipient=request.user).select_related('sender', 'sender__profile').order_by('-created_at')

    general_notifs.filter(is_seen=False).update(is_seen=True)

    return render(request, 'notification.html', {
        'friend_requests': f_requests,
        'notifications': general_notifs
    })

@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(recipient=request.user, is_seen=False).update(is_seen=True)
    return redirect('notifications')

@login_required
def get_unread_count(request):
    notif_count = Notification.objects.filter(recipient=request.user, is_seen=False).count()
    freq_count = FriendRequest.objects.filter(to_user=request.user).count()
    chat_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return JsonResponse({'notifications': notif_count + freq_count, 'chats': chat_count})

@login_required
def add_story(request):
    if request.method == "POST" and request.FILES.get('image'):
        Story.objects.create(
            user=request.user,
            image=request.FILES['image'],
            caption=request.POST.get('caption', '')
        )
        messages.success(request, "Story posted!")
    return redirect('home')

@login_required
def delete_story(request, story_id):
    story = get_object_or_404(Story, id=story_id, user=request.user)
    story.delete()
    return JsonResponse({'status': 'success'})

# --- ADMIN ACTIONS ---

@staff_member_required
def admin_broadcast_view(request):
    if request.method == "POST":
        msg_content = request.POST.get('message')
        if msg_content:
            setup_bots()
            try:
                broadcast_bot = User.objects.get(username='ThuTalkBot')
                all_users = User.objects.exclude(id=broadcast_bot.id)

                messages_to_send = [Message(sender=broadcast_bot, receiver=user, content=msg_content) for user in all_users]
                Message.objects.bulk_create(messages_to_send)

                messages.success(request, f"Broadcast sent to all users.")
            except User.DoesNotExist:
                messages.error(request, "Bot user not found.")
            return redirect('home')
    return render(request, 'admin_broadcast.html')

@staff_member_required
def ban_user(request, user_id):
    target = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        target.profile.is_banned = True
        target.profile.ban_reason = request.POST.get('reason', 'Violation of community standards')
        target.profile.ban_until = timezone.now() + timedelta(days=1)
        target.profile.save()
        messages.warning(request, f"{target.username} has been banned.")
    return redirect('profile_view', username=target.username)

@staff_member_required
def change_user_role(request, user_id):
    target = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        target.profile.role = request.POST.get('role', 'user')
        target.profile.save()
        messages.success(request, f"Role updated for {target.username}")
    return redirect('profile_view', username=target.username)

# --- MISC ---

@login_required
def edit_profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'edit_profile.html', {'profile': profile})

@login_required
def search_by_id(request):
    uid = request.GET.get('user_id')
    user = User.objects.filter(id=uid).first()
    if user:
        return redirect('profile_view', username=user.username)
    messages.error(request, "User not found")
    return redirect('home')

@login_required
def user_status_api(request, username):
    user = get_object_or_404(User, username=username)
    return JsonResponse({'is_online': user.profile.is_online()})