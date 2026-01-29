from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')), # myapp ရဲ့ urls.py ကို လှမ်းခေါ်တာပါ
]

# Media file (ပုံတွေ) ကြည့်လို့ရအောင် ထည့်ရပါမယ်
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)