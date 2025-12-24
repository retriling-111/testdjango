
from django.contrib import admin
from django.urls import path
from myapp import views      # myapp ထဲက view ကို ခေါ်လိုက်တာပါ

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'), # name='home' ထည့်ပေးပါ (redirect လုပ်ရင် သုံးဖို့ပါ)           # path အလွတ်က Home Page ကို ပြောတာပါ
    path('add/', views.add_profile, name='add_profile'), 
    path('profile/<int:pk>/', views.profile_detail, name='detail'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)