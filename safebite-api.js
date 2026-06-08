/**
 * SafeBite — API Client & Auth Utilities
 * المجلد المحدث ليتوافق مع نظام التحليل الذكي (Analyze Logic)
 * تم الربط بناءً على منطق الـ ID Intersection لضمان اكتشاف الحساسية بذكاء
 */

const API_BASE = "http://127.0.0.1:8000";
// ── Token Storage ─────────────────────────────────────────────────────────────
const Auth = {
  // جلب التوكن من التخزين المحلي
  getToken:   ()        => localStorage.getItem("token"),
  // حفظ التوكن عند تسجيل الدخول
  setToken:   (t)       => localStorage.setItem("token", t),

  // إدارة بيانات المستخدم الأساسية
  getUser:    ()        => JSON.parse(localStorage.getItem("user") || "null"),
  setUser:    (u)       => localStorage.setItem("user", JSON.stringify(u)),

  // مسح البيانات عند تسجيل الخروج أو انتهاء الجلسة
  clear:      ()        => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    localStorage.removeItem("user_allergies");
    localStorage.removeItem("user_full_name");
  },

  isLoggedIn: ()        => !!localStorage.getItem("token"),
};

// ── Base fetch wrapper ────────────────────────────────────────────────────────
/**
 * دالة موحدة لطلبات الـ API تقوم بإضافة التوكن تلقائياً ومعالجة الأخطاء
 */
async function apiFetch(path, options = {}) {
  const token = Auth.getToken();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };

  // حقن توكن الأمان في الهيدر إذا كان المستخدم مسجلاً
  if (token) headers["Authorization"] = `Bearer ${token}`;

  try {
    const res = await fetch(API_BASE + path, { ...options, headers });

    // إذا انتهت صلاحية التوكن (401 Unauthorized)
    if (res.status === 401) {
      Auth.clear();
      // منع التوجيه اللانهائي إذا كنا بالفعل في الصفحة الرئيسية
      if (!window.location.href.includes("index.html")) {
          window.location.href = "index.html";
      }
      return;
    }

    const data = await res.json().catch(() => ({}));

    // معالجة أخطاء السيرفر (مثل 404 للمنتج غير الموجود أو 400 للبيانات الخاطئة)
    if (!res.ok) throw new Error(data.detail || "Request failed");

    return data;
  } catch (err) {
    console.error("API Error:", err);
    throw err;
  }
}

// ── API Functions ─────────────────────────────────────────────────────────────

/**
 * تسجيل مستخدم جديد مع الملف الصحي والحساسية
 */
async function signUp(payload) {
    return apiFetch("/auth/signup", { method: "POST", body: JSON.stringify(payload) });
}

/**
 * تسجيل الدخول وحفظ بيانات الجلسة
 */
async function signIn(payload) {
    const data = await apiFetch("/auth/signin", { method: "POST", body: JSON.stringify(payload) });
    if (data && data.access_token) {
        Auth.setToken(data.access_token);
        Auth.setUser(data.user);
    }
    return data;
}

/**
 * جلب بيانات البروفايل (تستخدم في صفحة profile.html و global.js)
 */
async function getProfile() {
    return apiFetch("/profile/me");
}

/**
 * تحديث بيانات البروفايل أو الحساسية
 */
async function updateProfile(p) {
    return apiFetch("/profile/update", { method: "PUT", body: JSON.stringify(p) });
}

/**
 * جلب تاريخ الفحوصات ليعرض في البروفايل
 * تم توجيهه لـ /scanner/history لضمان جلب السجل المحدث
 */
async function getScanHistory() {
    return apiFetch("/scanner/history");
}

/**

 * يستخدم المسار /analyze بدلاً من /scan القديم.
 * هذا الاستدعاء يرسل الباركود للسيرفر ليقوم بمقارنة IDs الحساسية في بروفايلك
 * مع IDs الحساسية المرتبطة بالمنتج (مثل ربط الجبن بالألبان منطقياً).
 */
async function scanBarcode(bc) {
    return apiFetch(`/scanner/analyze/${bc}`, { method: "GET" });
}

/**
 * المساعد الذكي (Chatbot)
 */
async function askAI(message) {
    return apiFetch("/ai/ask", { method: "POST", body: JSON.stringify({ message }) });
}

// ── UI Helpers ─────────────────────────────────────────────────────────────

/**
 * تحديث أزرار الهيدر بناءً على حالة الدخول
 */
function updateNavAuth() {
  const loggedIn = Auth.isLoggedIn();
  const profileBtn = document.getElementById('profileBtn');
  const getStartedBtn = document.getElementById('getStartedBtn');

  if (profileBtn && getStartedBtn) {
    profileBtn.style.display = loggedIn ? 'inline-block' : 'none';
    getStartedBtn.style.display = loggedIn ? 'none' : 'inline-block';
  }
}

/**
 * حماية الصفحات التي تتطلب تسجيل دخول (مثل الماسح والبروفايل)
 */
function requireAuth() {
  if (!Auth.isLoggedIn()) {
    window.location.href = "index.html";
  }
}

/**
 * تسجيل الخروج والعودة للرئيسية
 */
function logout() {
    Auth.clear();
    window.location.href = "index.html";
}