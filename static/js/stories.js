let currentStoryIndex = 0;
let storyTimer;
let currentStories = [];
const STORY_DURATION = 5000; // ၅ စက္ကန့်စီ ပြသမည်

/**
 * Story Viewer ကို ဖွင့်လှစ်သည့် Function
 */
function openStory(storiesJson, startIndex = 0) {
    try {
        // HTML ကလာတဲ့ string ကို object ပြောင်းတာမှာ single quote/double quote error မတက်အောင် logic ထည့်ထားတယ်
        currentStories = JSON.parse(storiesJson);
    } catch (e) {
        console.error("Error parsing stories JSON:", e);
        return;
    }

    if (currentStories.length === 0) return;

    const viewer = document.getElementById('storyViewer');
    const progressContainer = document.getElementById('progressContainer');

    if (!viewer || !progressContainer) return;

    // Viewer ကို ပြသခြင်း
    viewer.style.display = 'block'; // Template ထဲမှာ display:none မို့ block ပြောင်းလိုက်တာ

    // Progress Bars များ အသစ်တည်ဆောက်ခြင်း
    progressContainer.innerHTML = '';
    currentStories.forEach(() => {
        const bar = document.createElement('div');
        bar.className = 'progress-bar'; // CSS ထဲမှာ style ရှိရမယ်
        bar.style.flex = "1";
        bar.style.height = "2px";
        bar.style.backgroundColor = "rgba(255,255,255,0.3)";
        bar.style.margin = "0 2px";
        bar.style.borderRadius = "2px";
        bar.style.overflow = "hidden";

        const fill = document.createElement('div');
        fill.className = 'progress-fill';
        fill.style.height = "100%";
        fill.style.width = "0%";
        fill.style.backgroundColor = "white";

        bar.appendChild(fill);
        progressContainer.appendChild(bar);
    });

    showStory(startIndex);
}

/**
 * သတ်မှတ်ထားသော Index အလိုက် Story ကို ပြသခြင်း
 */
function showStory(index) {
    if (index < 0) {
        showStory(0);
        return;
    }

    if (index >= currentStories.length) {
        closeStory();
        return;
    }

    currentStoryIndex = index;
    const story = currentStories[index];

    // UI Elements များကို Update လုပ်ခြင်း (Template ပါ ID များနှင့် ကိုက်အောင် ညှိထားသည်)
    const contentImg = document.getElementById('storyContent');
    const captionEl = document.getElementById('storyCaption');
    const usernameEl = document.getElementById('storyUsername');
    const avatarEl = document.getElementById('storyViewerAvatar');

    if (contentImg) contentImg.src = story.image_url;
    if (captionEl) captionEl.innerText = story.caption || '';
    if (usernameEl) usernameEl.innerText = story.user_username;
    if (avatarEl) avatarEl.src = story.user_avatar;

    // Delete Link Logic ပြင်ဆင်ခြင်း
    const deleteLink = document.getElementById('deleteStoryLink');
    if (deleteLink) {
        // story.user_id နဲ့ လက်ရှိ log-in ဝင်ထားသူ ID တူမှ ပြရန် (Template ထဲမှာပါတဲ့ global currentUserId ကိုသုံးသည်)
        if (typeof currentUserId !== 'undefined' && story.user_id == currentUserId) {
            deleteLink.parentElement.style.display = 'block';
            deleteLink.href = `/delete-story/${story.id}/`;
        } else {
            deleteLink.parentElement.style.display = 'none';
        }
    }

    // Progress Bar Animation Logic
    const fills = document.querySelectorAll('.progress-fill');
    fills.forEach((fill, i) => {
        fill.style.transition = 'none';
        if (i < index) {
            fill.style.width = '100%';
        } else {
            fill.style.width = '0%';
        }
    });

    // လက်ရှိ bar ကို animation စတင်ခြင်း
    setTimeout(() => {
        if (fills[index]) {
            fills[index].style.transition = `width ${STORY_DURATION}ms linear`;
            fills[index].style.width = '100%';
        }
    }, 50);

    // အချိန်ပြည့်လျှင် နောက်တစ်ခုသို့ အလိုအလျောက်ကူးခြင်း
    clearTimeout(storyTimer);
    storyTimer = setTimeout(() => showStory(index + 1), STORY_DURATION);
}

/**
 * Story Viewer ကို ပိတ်သိမ်းခြင်း
 */
function closeStory() {
    const viewer = document.getElementById('storyViewer');
    if (viewer) viewer.style.display = 'none';
    clearTimeout(storyTimer);

    // Progress များကို reset လုပ်ခြင်း
    const fills = document.querySelectorAll('.progress-fill');
    fills.forEach(fill => {
        fill.style.width = '0%';
        fill.style.transition = 'none';
    });
}

/**
 * Navigation Functions (ဘယ်/ညာ နှိပ်ခြင်းအတွက်)
 */
function nextStory() {
    showStory(currentStoryIndex + 1);
}

function prevStory() {
    showStory(currentStoryIndex - 1);
}

// Keyboard ပွဲအတွက် Event Listener
document.addEventListener('keydown', (e) => {
    const viewer = document.getElementById('storyViewer');
    if (viewer && viewer.style.display !== 'none') {
        if (e.key === 'ArrowRight') nextStory();
        if (e.key === 'ArrowLeft') prevStory();
        if (e.key === 'Escape') closeStory();
    }
});

// Screen Click Navigation Logic
document.addEventListener('DOMContentLoaded', () => {
    const storyViewer = document.getElementById('storyViewer');
    if (storyViewer) {
        storyViewer.addEventListener('click', (e) => {
            // အကယ်၍ Menu ခလုတ် သို့မဟုတ် Delete ခလုတ်ကို နှိပ်လျှင် story မကျော်စေရန်
            if (e.target.closest('.dropdown') || e.target.closest('.story-close')) return;

            const screenWidth = window.innerWidth;
            if (e.clientX < screenWidth / 3) {
                prevStory(); // ဘယ်ဘက် ၁ ပုံ ၃ ပုံကို နှိပ်လျှင် အနောက်သို့
            } else {
                nextStory(); // ကျန်သည့်နေရာကို နှိပ်လျှင် အရှေ့သို့
            }
        });
    }
});