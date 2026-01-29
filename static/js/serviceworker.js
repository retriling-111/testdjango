var staticCacheName = "django-pwa-v" + new Date().getTime();
var filesToCache = [
    '/offline/',
    '/static/Image/talk.jpeg', // Logo Path
    // CSS နဲ့ JS file အဓိကတွေကိုပါ cache လုပ်ထားရင် ပိုကောင်းပါတယ်
    // '/static/css/bootstrap.min.css',
];

// ၁။ Install လုပ်တဲ့အချိန် - အဓိက File တွေကို Cache ထဲ ထည့်မယ်
self.addEventListener("install", event => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(staticCacheName)
            .then(cache => {
                console.log("Caching essential files...");
                return cache.addAll(filesToCache);
            })
    );
});

// ၂။ Activate လုပ်တဲ့အချိန် - Cache အဟောင်းတွေကို ရှင်းထုတ်မယ်
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.filter(cacheName => {
                    return cacheName.startsWith("django-pwa-v") && cacheName !== staticCacheName;
                }).map(cacheName => {
                    return caches.delete(cacheName);
                })
            );
        })
    );
});

// ၃။ Fetch - Network ရှိရင် Network ကယူမယ်၊ မရှိရင် Cache ကယူမယ် (Network First with Cache Fallback)
// ဒါမှမဟုတ် Static file တွေအတွက်ဆိုရင် Cache First ကို သုံးမယ်
self.addEventListener("fetch", event => {
    // POST request တွေကို cache မလုပ်ပါနဲ့ (Django CSRF နဲ့ အဆင်မပြေဖြစ်တတ်လို့)
    if (event.request.method !== 'GET') return;

    event.respondWith(
        fetch(event.request)
            .then(response => {
                // Network အလုပ်လုပ်ရင် Cache ထဲကို အသစ်ပြန်ထည့်မယ် (Dynamic Caching)
                if (response.status === 200) {
                    let responseClone = response.clone();
                    caches.open(staticCacheName).then(cache => {
                        cache.put(event.request, responseClone);
                    });
                }
                return response;
            })
            .catch(() => {
                // Network မရှိရင် Cache ထဲက ရှာကြည့်မယ်
                return caches.match(event.request).then(response => {
                    if (response) {
                        return response;
                    }
                    // Cache ထဲမှာလည်း မရှိရင် Offline Page ပြမယ်
                    if (event.request.mode === 'navigate') {
                        return caches.match('/offline/');
                    }
                });
            })
    );
});