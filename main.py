import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

app = FastAPI()

API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/v1/chat/completions"

MODEL_NAME = "@cf/qwen/qwen3.8-27b"

# ==========================================
# 🎯 بخش تنظیمات پرامپت فوق‌تخصصی (نسخه جامع)
# ==========================================
SYSTEM_PROMPT = """
[هویت و نقش]
تو «مرهم» هستی؛ یک مشاور روانشناس و متخصص ارشد سلامت روان با ۲۰ سال تجربه بالینی. 
حوزه‌های تخصص تو شامل: روابط (خانوادگی، عاطفی، بین‌فردی)، مدیریت اضطراب و استرس، افسردگی خفیف، تقویت اعتماد به نفس و رشد فردی است.
تو تسلط کامل بر رویکرد «شناختی-رفتاری (CBT)»، «ارتباط بدون خشونت (NVC)» و «نظریه دلبستگی» داری.
تو یک درمانگر بالینی نیستی و حق تشخیص بیماری یا تجویز دارو نداری.

[لحن و شخصیت]
- لحن تو باید بسیار آرام، گرم، همدلانه، بدون قضاوت و سرشار از اطمینان‌بخشی باشد. (مثل یک پناهگاه امن).
- هرگز طرف کسی را نگیر و از کلمات کلیشه‌ای و رباتیک استفاده نکن. مثل یک انسان دانا و مهربان صحبت کن.

[اصول درمانی که باید رعایت کنی]
۱. اعتباربخشی (Validation): همیشه ابتدا احساس کاربر را ببین و تایید کن که حق دارد چنین حسی داشته باشد.
۲. کشف ریشه (Root Cause): احساسات منفی معمولاً پوششی برای نیازهای برآورده‌نشده هستند. سعی کن نیاز پنهان کاربر را کشف کنی.
۳. ابزار عملی: از تکنیک‌های CBT و NVC برای ارائه راهکار عملی استفاده کن.
۴. سوالات سقراطی: به جای نصیحت مستقیم، با سوالات عمیق کاربر را به خودآگاهی برسان.

[ساختار پاسخ‌دهی]
پاسخ‌ها باید همیشه از این الگوی ۳ مرحله‌ای پیروی کنند:
1. **آینه‌سازی و همدلی:** یک پاراگراف کوتاه برای درک عمیق احساسات.
2. **بازتعریف یا ارائه ابزار:** یک زاویه دید جدید یا یک تکنیک عملی. (اگر از مثال یا نقل‌قول استفاده می‌کنی، حتماً آن را کامل و با علامت گیومه «...» ببند).
3. **سوال پایانی:** یک سوال کوتاه و هوشمندانه برای ادامه مسیر.

[خط قرمزها - بسیار مهم]
- پاسخ‌ها باید روان و در حد ۲ تا ۳ پاراگراف کوتاه باشند.
- **تحت هیچ شرایطی جمله، نقل‌قول یا لیست خود را نیمه‌کاره رها نکن. پاسخ تو باید حتماً با نقطه (.)، علامت سوال (؟) یا بستن گیومه («) به پایان برسد.**
- اگر کاربر نشانه‌های آزار و اذیت شدید، خودکشی یا بحران حاد را نشان داد، با دلسوزی او را به اورژانس اجتماعی (۱۲۳) یا صدای مشاور (۱۴۸۰) ارجاع بده.
"""
# ==========================================

class ChatRequest(BaseModel):
    messages: list
    profile_id: str

@app.post("/chat")
async def chat(request: ChatRequest):
    if not API_TOKEN or not ACCOUNT_ID:
        raise HTTPException(status_code=500, detail="کلیدهای API در ورسل تنظیم نشده‌اند.")
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
        "x-session-affinity": request.profile_id
    }
    
    system_message = {"role": "system", "content": SYSTEM_PROMPT}
    
    payload = {
        "model": MODEL_NAME,
        "messages": [system_message] + request.messages,
        "max_tokens": 3048, # 👈 افزایش شدید فضا برای جلوگیری از قطع شدن جملات
        "temperature": 0.75 
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=240)
        response.raise_for_status() 
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            reply_text = choice["message"]["content"]
            finish_reason = choice.get("finish_reason", "")
            
            # بررسی اینکه آیا مدل به دلیل محدودیت توکن نصفه مونده یا نه
            if finish_reason == "length":
                reply_text += "\n\n*(پاسخ به دلیل طولانی شدن قطع شد. لطفاً از من بخواهید ادامه دهم.)*"

            if not reply_text or len(reply_text.strip()) < 10:
                reply_text = "من کاملاً درکت می‌کنم. دوست داری بیشتر در این مورد صحبت کنیم؟"
            return {"reply": reply_text}
        else:
            return {"reply": "متاسفانه الان نمی‌تونم پاسخ بدم. دوباره تلاش می‌کنی؟"}
            
    except Exception as e:
        error_detail = response.text if 'response' in locals() else str(e)
        raise HTTPException(status_code=500, detail=f"خطا در ارتباط با کلادفلر: {error_detail}")

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
            <title>مرهم | همراه و مشاور شما</title>
            <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700&display=swap');
                
                :root {
                    --bg-body: #f0f2f5; --sidebar-bg: #ffffff; --chat-bg: #f7f9fc;
                    --primary: #4f46e5; --primary-hover: #4338ca;
                    --text-main: #1f2937; --text-muted: #6b7280;
                    --user-bubble: #e0e7ff; --ai-bubble: #ffffff; --border-color: #e5e7eb;
                }
                
                html, body { height: 100%; margin: 0; padding: 0; overflow: hidden; background-color: var(--bg-body); }
                body { font-family: 'Vazirmatn', Tahoma, sans-serif; display: flex; color: var(--text-main); }
                
                ::-webkit-scrollbar { width: 6px; }
                ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }

                .profile-screen {
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                    background: linear-gradient(135deg, #f0f2f5 0%, #e0e7ff 100%);
                    display: flex; flex-direction: column; align-items: center; justify-content: center;
                    z-index: 1000; padding: 20px; box-sizing: border-box; overflow-y: auto;
                }
                .profile-card {
                    background: white; padding: 30px; border-radius: 24px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.08); width: 100%; max-width: 400px;
                    text-align: center; margin: auto;
                }
                .profile-logo { font-size: 50px; margin-bottom: 10px; }
                .profile-title { color: var(--primary); margin: 0 0 10px 0; font-size: 24px; }
                .profile-subtitle { color: var(--text-muted); font-size: 14px; margin-bottom: 25px; }
                
                .input-group { display: flex; flex-direction: column; gap: 15px; }
                .input-group input {
                    padding: 15px; border: 2px solid var(--border-color); border-radius: 12px;
                    font-family: inherit; font-size: 15px; outline: none; transition: border 0.3s; text-align: center;
                }
                .input-group input:focus { border-color: var(--primary); }
                .btn-primary {
                    padding: 15px; background: var(--primary); color: white; border: none;
                    border-radius: 12px; font-family: inherit; font-size: 16px; font-weight: 700; cursor: pointer;
                }
                .btn-primary:hover { background: var(--primary-hover); }

                .profile-list {
                    margin-top: 25px; border-top: 1px solid var(--border-color); padding-top: 20px;
                    display: flex; flex-direction: column; gap: 10px; max-height: 250px; overflow-y: auto;
                }
                .profile-item {
                    display: flex; align-items: center; justify-content: space-between; padding: 12px;
                    border-radius: 12px; background: #f9fafb; cursor: pointer; border: 1px solid var(--border-color);
                    transition: all 0.2s;
                }
                .profile-item:hover { background: #f3f4f6; border-color: #d1d5db; }
                .profile-info { display: flex; align-items: center; gap: 12px; }
                .profile-avatar-mini {
                    width: 35px; height: 35px; border-radius: 50%; background: linear-gradient(135deg, #818cf8, #4f46e5);
                    color: white; display: flex; align-items: center; justify-content: center; font-weight: bold;
                }
                .delete-profile-btn {
                    color: #ef4444; font-size: 18px; padding: 5px; opacity: 0.5;
                    transition: all 0.2s; border-radius: 50%; width: 30px; height: 30px;
                    display: flex; align-items: center; justify-content: center;
                }
                .profile-item:hover .delete-profile-btn { opacity: 1; background: #fee2e2; }

                .main-app { display: flex; width: 100%; height: 100dvh; }
                .sidebar {
                    width: 280px; background-color: var(--sidebar-bg); border-left: 1px solid var(--border-color);
                    display: flex; flex-direction: column; height: 100dvh; z-index: 100;
                }
                .sidebar-header { padding: 20px; font-weight: 700; font-size: 18px; color: var(--primary); display: flex; gap: 8px; }
                .user-info-box {
                    margin: 0 15px 15px 15px; padding: 12px; background: #f3f4f6; border-radius: 12px;
                    display: flex; align-items: center; justify-content: space-between;
                }
                .user-info-name { font-size: 14px; font-weight: 700; }
                .switch-profile-btn { background: transparent; border: none; color: var(--primary); font-size: 12px; cursor: pointer; }
                .switch-profile-btn:hover { text-decoration: underline; }
                
                .new-chat-btn-sidebar {
                    margin: 0 15px 15px 15px; padding: 12px; background-color: var(--primary); border: none;
                    border-radius: 12px; font-family: inherit; font-size: 14px; color: #ffffff; cursor: pointer;
                    display: flex; align-items: center; justify-content: center; gap: 8px;
                }
                .chat-list { flex: 1; overflow-y: auto; padding: 0 10px; }
                .chat-item {
                    padding: 12px; margin-bottom: 4px; border-radius: 10px; cursor: pointer; font-size: 14px;
                    display: flex; justify-content: space-between; align-items: center;
                }
                .chat-item:hover { background-color: #f3f4f6; }
                .chat-item.active { background-color: #f3f4f6; font-weight: 700; color: var(--primary); }
                .delete-chat-icon { color: #ef4444; opacity: 0; padding: 4px; font-size: 14px;}
                .chat-item:hover .delete-chat-icon { opacity: 1; }

                .main-chat {
                    flex: 1; display: flex; flex-direction: column; background-color: var(--chat-bg);
                    background-image: radial-gradient(#e5e7eb 1px, transparent 1px); background-size: 20px 20px;
                    height: 100dvh;
                }
                .tg-header { background-color: rgba(255, 255, 255, 0.85); backdrop-filter: blur(10px); padding: 12px 20px; display: flex; align-items: center; border-bottom: 1px solid var(--border-color); }
                .menu-btn { display: none; background: transparent; border: none; font-size: 24px; cursor: pointer; margin-left: 15px; }
                .header-profile { display: flex; align-items: center; }
                .header-avatar { width: 46px; height: 46px; border-radius: 50%; background: linear-gradient(135deg, #818cf8, #4f46e5); color: white; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-left: 15px; }
                .header-info h2 { margin: 0; font-size: 18px; color: var(--primary); }
                .header-info p { margin: 4px 0 0 0; font-size: 13px; color: var(--text-muted); }

                .tg-messages { flex: 1; padding: 25px 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; }
                .message-row { display: flex; align-items: flex-end; width: 100%; }
                .message-row.user { justify-content: flex-start; flex-direction: row-reverse; }
                .message-content { max-width: 75%; display: flex; flex-direction: column; }
                .message-bubble { padding: 14px 18px; border-radius: 18px; line-height: 1.7; font-size: 15px; position: relative; animation: slideUp 0.3s ease-out forwards; }
                .message-bubble p { margin: 0 0 10px 0; }
                .message-bubble p:last-child { margin-bottom: 0; }
                .message-bubble strong { font-weight: 700; color: var(--primary); }
                .message-row.user .message-bubble { background-color: var(--user-bubble); color: #1e1b4b; border-top-right-radius: 4px; border-bottom-left-radius: 18px; border-bottom-right-radius: 18px; }
                .message-row.ai .message-bubble { background-color: var(--ai-bubble); border: 1px solid var(--border-color); border-top-left-radius: 4px; border-bottom-left-radius: 18px; border-bottom-right-radius: 18px; }
                .copy-btn { position: absolute; bottom: -24px; left: 10px; background: transparent; border: none; color: #9ca3af; font-size: 12px; cursor: pointer; opacity: 0; }
                .message-row.ai:hover .copy-btn { opacity: 1; }
                
                .input-wrapper { padding: 10px 20px 20px 20px; background: linear-gradient(to top, var(--chat-bg) 70%, transparent); }
                .tg-input-area { display: flex; padding: 6px 10px; background-color: #ffffff; align-items: flex-end; border-radius: 24px; box-shadow: 0 5px 20px rgba(0,0,0,0.06); border: 1px solid var(--border-color); }
                .tg-input-area:focus-within { border-color: #a5b4fc; }
                .tg-input-area textarea { flex: 1; padding: 12px 16px; border: none; background-color: transparent; border-radius: 18px; outline: none; font-family: inherit; font-size: 15px; resize: none; max-height: 150px; line-height: 1.5; }
                .tg-send-btn { width: 44px; height: 44px; margin: 2px; background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; border: none; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; }
                .tg-send-btn:disabled { background: #e5e7eb; color: #9ca3af; cursor: not-allowed; }
                .typing-indicator { display: flex; gap: 5px; padding: 16px 20px; background: var(--ai-bubble); border: 1px solid var(--border-color); border-radius: 18px; border-top-left-radius: 4px; }
                .typing-indicator span { width: 6px; height: 6px; background-color: #a5b4fc; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; }
                @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
                @keyframes slideUp { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }

                @media (max-width: 768px) {
                    .sidebar { position: fixed; right: 0; top: 0; transform: translateX(100%); transition: transform 0.3s ease; box-shadow: -5px 0 25px rgba(0,0,0,0.1); }
                    .sidebar.open { transform: translateX(0); }
                    .menu-btn { display: block; }
                    .message-content { max-width: 88%; }
                    .input-wrapper { padding: 10px 15px 15px 15px; }
                }
            </style>
        </head>
        <body>
            
            <div class="profile-screen" id="profile-screen">
                <div class="profile-card">
                    <div class="profile-logo">🍃</div>
                    <h1 class="profile-title">به مرهم خوش آمدید</h1>
                    <p class="profile-subtitle">برای شروع، نام خود را وارد کنید تا پروفایل شما ساخته شود.</p>
                    <div class="input-group">
                        <input type="text" id="profile-name-input" placeholder="نام شما (مثلاً: علی)" autocomplete="off">
                        <button class="btn-primary" onclick="createProfile()">ورود به مرهم</button>
                    </div>
                    <div class="profile-list" id="profile-list" style="display: none;">
                        <p style="font-size: 13px; color: var(--text-muted); margin: 0 0 10px 0;">یا از پروفایل‌های قبلی انتخاب کنید:</p>
                    </div>
                </div>
            </div>

            <div class="main-app" id="main-app" style="display: none;">
                <div class="sidebar" id="sidebar">
                    <div class="sidebar-header"><span>🍃</span> مرهم</div>
                    <div class="user-info-box">
                        <span class="user-info-name" id="sidebar-username">کاربر</span>
                        <button class="switch-profile-btn" onclick="logout()">تغییر پروفایل</button>
                    </div>
                    <button class="new-chat-btn-sidebar" onclick="createNewChat()"><span>+</span> گفتگوی جدید</button>
                    <div class="chat-list" id="chat-list"></div>
                </div>

                <div class="main-chat">
                    <div class="tg-header">
                        <button class="menu-btn" onclick="toggleSidebar()">☰</button>
                        <div class="header-profile">
                            <div class="header-avatar">🍃</div>
                            <div class="header-info">
                                <h2>مرهم</h2>
                                <p id="header-greeting">همراه و مشاور شما</p>
                            </div>
                        </div>
                    </div>
                    <div class="tg-messages" id="chat-box"></div>
                    <div class="input-wrapper">
                        <div class="tg-input-area">
                            <textarea id="msg" placeholder="هر چیزی که در ذهنت هست را بنویس..." rows="1"></textarea>
                            <button class="tg-send-btn" id="send-btn" onclick="send()">
                                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                const chatBox = document.getElementById('chat-box');
                const msgInput = document.getElementById('msg');
                const chatListDiv = document.getElementById('chat-list');
                const sidebar = document.getElementById('sidebar');

                let profiles = [];
                let currentProfileId = null;
                let currentProfileName = "";
                let allChats = [];
                let currentChatId = null;

                function migrateOldData() {
                    const oldData = localStorage.getItem('marhamAppData');
                    if (oldData && !localStorage.getItem('marhamProfiles')) {
                        try {
                            const parsed = JSON.parse(oldData);
                            const defaultProfile = { id: 'usr_default', name: 'کاربر من', createdAt: Date.now() };
                            localStorage.setItem('marhamProfiles', JSON.stringify([defaultProfile]));
                            localStorage.setItem('marhamActiveProfile', 'usr_default');
                            localStorage.setItem('marhamChats_usr_default', JSON.stringify(parsed));
                            localStorage.removeItem('marhamAppData');
                        } catch (e) {}
                    }
                }

                function initProfileSystem() {
                    migrateOldData();
                    const savedProfiles = localStorage.getItem('marhamProfiles');
                    const activeProfileId = localStorage.getItem('marhamActiveProfile');

                    if (savedProfiles) {
                        profiles = JSON.parse(savedProfiles);
                        renderProfileList();
                    }

                    if (activeProfileId && profiles.find(p => p.id === activeProfileId)) {
                        loginToProfile(activeProfileId);
                    } else {
                        document.getElementById('profile-screen').style.display = 'flex';
                        document.getElementById('main-app').style.display = 'none';
                    }
                }

                function renderProfileList() {
                    const listDiv = document.getElementById('profile-list');
                    if (profiles.length === 0) {
                        listDiv.style.display = 'none';
                        return;
                    }
                    
                    listDiv.style.display = 'block';
                    while(listDiv.children.length > 1) {
                        listDiv.removeChild(listDiv.lastChild);
                    }

                    profiles.forEach(p => {
                        const item = document.createElement('div');
                        item.className = 'profile-item';
                        
                        const infoDiv = document.createElement('div');
                        infoDiv.className = 'profile-info';
                        
                        const avatar = document.createElement('div');
                        avatar.className = 'profile-avatar-mini';
                        avatar.innerText = p.name.charAt(0).toUpperCase();
                        
                        const name = document.createElement('span');
                        name.innerText = p.name;

                        infoDiv.appendChild(avatar);
                        infoDiv.appendChild(name);
                        infoDiv.onclick = () => loginToProfile(p.id);

                        const delBtn = document.createElement('span');
                        delBtn.className = 'delete-profile-btn';
                        delBtn.innerHTML = '✕';
                        delBtn.title = "حذف پروفایل";
                        delBtn.onclick = (e) => {
                            e.stopPropagation();
                            deleteProfile(p.id);
                        };

                        item.appendChild(infoDiv);
                        item.appendChild(delBtn);
                        listDiv.appendChild(item);
                    });
                }

                function createProfile() {
                    const nameInput = document.getElementById('profile-name-input');
                    const name = nameInput.value.trim();
                    if (!name) {
                        alert("لطفاً یک نام وارد کنید.");
                        return;
                    }

                    const newProfile = {
                        id: 'usr_' + Date.now(),
                        name: name,
                        createdAt: Date.now()
                    };

                    profiles.push(newProfile);
                    localStorage.setItem('marhamProfiles', JSON.stringify(profiles));
                    nameInput.value = '';
                    
                    loginToProfile(newProfile.id);
                }

                function deleteProfile(profileId) {
                    if (confirm("آیا مطمئن هستید که می‌خواهید این پروفایل و تمام چت‌های مربوط به آن را برای همیشه حذف کنید؟")) {
                        profiles = profiles.filter(p => p.id !== profileId);
                        localStorage.setItem('marhamProfiles', JSON.stringify(profiles));
                        localStorage.removeItem('marhamChats_' + profileId);
                        
                        if (currentProfileId === profileId) {
                            logout();
                        } else {
                            renderProfileList();
                        }
                    }
                }

                function loginToProfile(profileId) {
                    currentProfileId = profileId;
                    const profile = profiles.find(p => p.id === profileId);
                    if(!profile) return;
                    
                    currentProfileName = profile.name;
                    localStorage.setItem('marhamActiveProfile', currentProfileId);

                    document.getElementById('profile-screen').style.display = 'none';
                    document.getElementById('main-app').style.display = 'flex';

                    document.getElementById('sidebar-username').innerText = currentProfileName;
                    document.getElementById('header-greeting').innerText = `سلام ${currentProfileName} عزیز، خوش آمدی`;

                    loadUserChats();
                }

                function logout() {
                    localStorage.removeItem('marhamActiveProfile');
                    currentProfileId = null;
                    currentProfileName = "";
                    document.getElementById('main-app').style.display = 'none';
                    document.getElementById('profile-screen').style.display = 'flex';
                    renderProfileList();
                }

                function getStorageKey() {
                    return `marhamChats_${currentProfileId}`;
                }

                function loadUserChats() {
                    const savedData = localStorage.getItem(getStorageKey());
                    if (savedData) {
                        const parsed = JSON.parse(savedData);
                        allChats = parsed.chats || [];
                        currentChatId = parsed.currentChatId;
                    } else {
                        allChats = [];
                        currentChatId = null;
                    }

                    if (allChats.length === 0) {
                        createNewChat();
                    } else {
                        if (!currentChatId || !allChats.find(c => c.id === currentChatId)) {
                            currentChatId = allChats[0].id;
                        }
                        loadChat(currentChatId);
                    }
                }

                function saveData() {
                    if (!currentProfileId) return;
                    const dataToSave = { chats: allChats, currentChatId: currentChatId };
                    localStorage.setItem(getStorageKey(), JSON.stringify(dataToSave));
                }

                function renderSidebar() {
                    chatListDiv.innerHTML = '';
                    allChats.sort((a, b) => b.timestamp - a.timestamp);
                    
                    allChats.forEach(chat => {
                        const item = document.createElement('div');
                        item.className = `chat-item ${chat.id === currentChatId ? 'active' : ''}`;
                        
                        const titleSpan = document.createElement('span');
                        titleSpan.innerText = chat.title;
                        
                        const deleteBtn = document.createElement('span');
                        deleteBtn.className = 'delete-chat-icon';
                        deleteBtn.innerText = '✕';
                        deleteBtn.title = "حذف گفتگو";
                        deleteBtn.onclick = (e) => {
                            e.stopPropagation();
                            deleteChat(chat.id);
                        };

                        item.appendChild(titleSpan);
                        item.appendChild(deleteBtn);
                        
                        item.onclick = () => {
                            loadChat(chat.id);
                            if (window.innerWidth <= 768) toggleSidebar();
                        };
                        
                        chatListDiv.appendChild(item);
                    });
                }

                function createNewChat() {
                    const newId = 'chat_' + Date.now();
                    const greetingWithName = `سلام ${currentProfileName} عزیز! من «مرهم» هستم. امروز چه چیزی ذهن تو را مشغول کرده؟`;
                    
                    const newChat = {
                        id: newId,
                        title: "گفتگوی جدید",
                        messages: [{ role: 'assistant', content: greetingWithName }],
                        timestamp: Date.now()
                    };
                    
                    allChats.unshift(newChat);
                    currentChatId = newId;
                    
                    saveData();
                    renderSidebar();
                    loadChat(newId);
                    
                    if (window.innerWidth <= 768 && sidebar.classList.contains('open')) {
                        toggleSidebar();
                    }
                }

                function loadChat(chatId) {
                    currentChatId = chatId;
                    const chat = allChats.find(c => c.id === chatId);
                    if (!chat) return;

                    chatBox.innerHTML = '';
                    chat.messages.forEach(msg => {
                        appendMessageUI(msg.role === 'user' ? 'user' : 'ai', msg.content, false);
                    });
                    
                    chatBox.scrollTop = chatBox.scrollHeight;
                    renderSidebar();
                    saveData();
                }

                function deleteChat(chatId) {
                    if (confirm("آیا مطمئن هستید که می‌خواهید این گفتگو را برای همیشه حذف کنید؟")) {
                        allChats = allChats.filter(c => c.id !== chatId);
                        if (currentChatId === chatId) {
                            if (allChats.length > 0) {
                                currentChatId = allChats[0].id;
                                loadChat(currentChatId);
                            } else {
                                createNewChat();
                            }
                        } else {
                            saveData();
                            renderSidebar();
                        }
                    }
                }

                function toggleSidebar() {
                    sidebar.classList.toggle('open');
                }

                msgInput.addEventListener('input', function() {
                    this.style.height = 'auto';
                    this.style.height = (this.scrollHeight) + 'px';
                    if(this.value === '') this.style.height = 'auto';
                });

                async function send() {
                    const msg = msgInput.value.trim();
                    if (!msg || !currentChatId) return;

                    msgInput.style.height = 'auto';
                    msgInput.value = '';
                    
                    let currentChat = allChats.find(c => c.id === currentChatId);
                    
                    appendMessageUI('user', msg);
                    currentChat.messages.push({ role: 'user', content: msg });
                    
                    if (currentChat.messages.length === 2 && currentChat.title === "گفتگوی جدید") {
                        currentChat.title = msg.substring(0, 25) + (msg.length > 25 ? '...' : '');
                    }
                    
                    currentChat.timestamp = Date.now();
                    saveData();
                    renderSidebar();

                    const apiMessages = currentChat.messages.slice(-12);
                    const typingId = showTypingIndicator();
                    const sendBtn = document.getElementById('send-btn');
                    sendBtn.disabled = true;
                    
                    try {
                        const res = await fetch('/chat', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ 
                                messages: apiMessages,
                                profile_id: currentProfileId 
                            })
                        });
                        const data = await res.json();
                        const reply = data.reply || data.detail || "خطای نامشخص";

                        removeTypingIndicator(typingId);
                        appendMessageUI('ai', reply);
                        
                        currentChat.messages.push({ role: 'assistant', content: reply });
                        currentChat.timestamp = Date.now();
                        saveData();

                    } catch(e) {
                        removeTypingIndicator(typingId);
                        appendMessageUI('ai', "ارتباط برقرار نشد. دوباره تلاش کنید.");
                    } finally {
                        sendBtn.disabled = false;
                    }
                }

                function appendMessageUI(role, text, scroll = true) {
                    if (!text || !text.trim()) return; 
                    const row = document.createElement('div');
                    row.className = `message-row ${role}`;
                    const content = document.createElement('div');
                    content.className = 'message-content';
                    const bubble = document.createElement('div');
                    bubble.className = 'message-bubble';
                    
                    if (role === 'ai') {
                        bubble.innerHTML = marked.parse(text);
                        const copyBtn = document.createElement('button');
                        copyBtn.className = 'copy-btn';
                        copyBtn.innerHTML = '📋 کپی متن';
                        copyBtn.onclick = () => {
                            navigator.clipboard.writeText(text);
                            copyBtn.innerHTML = '✓ کپی شد';
                            setTimeout(() => copyBtn.innerHTML = '📋 کپی متن', 2000);
                        };
                        bubble.appendChild(copyBtn);
                    } else {
                        bubble.innerText = text;
                    }
                    
                    content.appendChild(bubble);
                    row.appendChild(content);
                    chatBox.appendChild(row);
                    if (scroll) chatBox.scrollTop = chatBox.scrollHeight; 
                }

                function showTypingIndicator() {
                    const id = 'typing-' + Date.now();
                    const row = document.createElement('div');
                    row.className = 'message-row ai';
                    row.id = id;
                    
                    const content = document.createElement('div');
                    content.className = 'message-content';
                    const typing = document.createElement('div');
                    typing.className = 'typing-indicator';
                    typing.innerHTML = '<span></span><span></span><span></span>';
                    
                    content.appendChild(typing);
                    row.appendChild(content);
                    chatBox.appendChild(row);
                    chatBox.scrollTop = chatBox.scrollHeight;
                    return id;
                }

                function removeTypingIndicator(id) {
                    const el = document.getElementById(id);
                    if (el) el.remove();
                }

                window.onload = initProfileSystem;
            </script>
        </body>
    </html>
    """
