/**
 * SafeBite — Global Logic & Persistence
 */

const API_BASE = "http://127.0.0.1:8000";
async function syncAndInjectProfile() {
    const token = localStorage.getItem('token');

    // إذا لم يسجل المستخدم دخوله، لا نفعل شيئاً (أو يمكن توجيهه لصفحة الدخول)
    if (!token) {
        console.warn("No active session found.");
        return;
    }

    try {
        const response = await fetch(`${GLOBAL_API_BASE}/profile/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const user = await response.json();

            // 1. تخزين الحساسية والبيانات المهمة محلياً لسرعة الوصول في كل الصفحات
            localStorage.setItem('user_full_name', user.full_name);
            localStorage.setItem('user_allergies', JSON.stringify(user.allergies));

            // 2. تحديث شريط التنقل (Navbar) تلقائياً
            updateNavbarUI(user);
        } else {
            // إذا التوكن منتهي الصلاحية
            console.error("Session expired.");
            // localStorage.clear();
        }
    } catch (error) {
        console.error("Global Sync Error:", error);
    }
}

function updateNavbarUI(user) {
    const navInner = document.querySelector('.nav-inner');
    if (!navInner) return;

    // استخراج الحرف الأول من الاسم للأيقونة
    const firstLetter = user.full_name ? user.full_name[0].toUpperCase() : "U";
    const shortName = user.full_name ? user.full_name.split(' ')[0] : "User";

    // كود HTML لأيقونة البروفايل في الزاوية
    const profileWidgetHTML = `
        <div class="global-profile-widget" onclick="window.location.href='profile.html'">
            <div class="profile-info-text">
                <span class="welcome-text">Welcome,</span>
                <span class="user-display-name">${shortName}</span>
            </div>
            <div class="global-avatar">${firstLetter}</div>
        </div>
    `;

    // منع التكرار: ابحث عن العنصر إذا كان موجوداً سابقاً وحدثه، أو أضفه
    const existingWidget = document.querySelector('.global-profile-widget');
    if (existingWidget) {
        existingWidget.outerHTML = profileWidgetHTML;
    } else {
        navInner.insertAdjacentHTML('beforeend', profileWidgetHTML);
    }
}

// تشغيل المزامنة فور تحميل أي صفحة مرتبطة بهذا الملف
document.addEventListener('DOMContentLoaded', syncAndInjectProfile);