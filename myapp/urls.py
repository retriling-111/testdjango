import os
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # --- Authentication ---
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # --- Core & Notifications ---
    path('', views.home, name='home'),
    path('search/', views.search_page, name='search_page'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('get_unread_count/', views.get_unread_count, name='get_unread_count'),

    # --- Posts & Real-time Interaction (AJAX) ---
    path('post/add/', views.add_post, name='add_post'),
    path('post/edit/<int:pk>/', views.edit_post, name='edit_post'),
    path('post/delete/<int:pk>/', views.delete_post, name='delete_post'),
    path('like/<int:pk>/', views.like_post, name='like_post'),
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),

    # --- Story System ---
    path('story/add/', views.add_story, name='add_story'),
    path('delete-story/<int:story_id>/', views.delete_story, name='delete_story'),

    # --- Profile & Social ---
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/<str:username>/', views.profile_view, name='profile_view'),
    path('profile/<str:username>/friends/', views.all_friends_view, name='all_friends_view'),
    path('block/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('unfriend/<int:user_id>/', views.unfriend_user, name='unfriend_user'),
    path('search-by-id/', views.search_by_id, name='search_by_id'),

    # --- Friend System ---
    path('friend/request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friend/accept/<int:request_id>/', views.accept_friend, name='accept_friend'),
    path('friend/delete/<int:request_id>/', views.delete_request, name='delete_request'),
    path('friend/cancel/<int:user_id>/', views.cancel_friend_request, name='cancel_friend_request'),

    # --- Chat System & APIs ---
    path('chats/', views.chat_list, name='chat_list'),
    path('chat/<str:username>/', views.chat_room, name='chat_room'),
    path('chat/profile/<str:username>/', views.chat_profile_view, name='chat_profile'),
    path('chat/search/<str:username>/', views.search_messages, name='search_messages'),
    path('api/send_message/<str:username>/', views.send_message, name='send_message'),
    path('api/get_messages/<str:username>/', views.get_messages, name='get_messages'),
    path('api/user_status/<str:username>/', views.user_status_api, name='user_status_api'),
    path('chat/edit_message/<int:message_id>/', views.edit_message, name='edit_message'),
    path('chat/delete_message/<int:message_id>/', views.delete_message, name='delete_message'),

    # --- Settings ---
    path('settings/', views.settings_view, name='settings'),
    path('settings/update/', views.update_profile_ajax, name='update_profile'),
    path('settings/password/', views.change_password, name='change_password'),
    path('settings/delete/', views.delete_account, name='delete_account'),

    # --- Admin Actions ---
    path('admin/ban-user/<int:user_id>/', views.ban_user, name='ban_user'),
    path('admin/change-role/<int:user_id>/', views.change_user_role, name='change_user_role'),
    path('official-broadcast/', views.admin_broadcast_view, name='admin_broadcast'),
]

# Media & Static Files handling
# Development ရော Production မှာပါ static/media ဖိုင်တွေ မြင်ရအောင် ပေါင်းထည့်ပေးထားပါတယ်
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)