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
# 🎯 بخش تنظیمات پرامپت
# ==========================================
SYSTEM_PROMPT = (
    "تو یک مشاور متخصص روابط (خانوادگی و عاطفی) با رویکرد شناختی-رفتاری (CBT) و ارتباط بدون خشونت (NVC) هستی. "
    "لحن تو همدلانه، آرام و بدون قضاوت است. کاربر هدفی دارد و تو باید او را به سمت این هدف هدایت کنی.\n\n"
    "قوانین کلیدی:\n"
    "۱. همدلی: احساسات کاربر (مثل نفرت یا بی‌اعتمادی) را کاملاً تایید کن.\n"
    "۲. هدایت: بعد از تایید، کاربر را به سمت هدفش (بهبود رابطه) برگردان.\n"
    "۳. ابزار عملی: تکنیک‌های ارتباطی (مثل جملات «من») را به او یاد بده.\n"
    "۴. طول پاسخ: پاسخ‌ها باید بسیار روان و کوتاه باشند (حداکثر ۱۵۰ کلمه). از نوشتن متن‌های طولانی خودداری کن.\n"
    "۵. سوال نهایی: هرگز پاسخ را نیمه‌کاره رها نکن. در انتهای هر پیام، حتماً یک سوال کوتاه بپرس."
)
# ==========================================

class ChatRequest(BaseModel):
    messages: list

@app.post("/chat")
async def chat(request: ChatRequest):
    if not API_TOKEN or not ACCOUNT_ID:
        raise HTTPException(status_code=500, detail="کلیدهای API در ورسل تنظیم نشده‌اند.")
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    system_message = {"role": "system", "content": SYSTEM_PROMPT}
    
    payload = {
        "model": MODEL_NAME,
        "messages": [system_message] + request.messages,
        "max_tokens": 800,
        "temperature": 0.75 
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status() 
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            reply_text = data["choices"][0]["message"]["content"]
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
            <title>مشاور هوش مصنوعی</title>
            <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;700&display=swap');
                
                html, body { height: 100%; margin: 0; padding: 0; overflow: hidden; background-color: #f7f7f8; }
                
                body { 
                    font-family: 'Vazirmatn', Tahoma, sans-serif; 
                    display: flex; 
                }
                
                /* ========================================== */
                /* 🗂️ نوار کناری (Sidebar) - شبیه ChatGPT */
                /* ========================================== */
                .sidebar {
                    width: 260px;
                    background-color: #f9f9f9;
                    border-left: 1px solid #e0e0e0;
                    display: flex;
                    flex-direction: column;
                    height: 100dvh;
                    transition: transform 0.3s ease;
                    z-index: 100;
                }
                
                .new-chat-btn-sidebar {
                    margin: 15px;
                    padding: 12px;
                    background-color: #ffffff;
                    border: 1px solid #d1d5db;
                    border-radius: 8px;
                    font-family: inherit;
                    font-size: 14px;
                    font-weight: 700;
                    color: #374151;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                    transition: background 0.2s;
                }
                .new-chat-btn-sidebar:hover { background-color: #f3f4f6; }

                .chat-list {
                    flex: 1;
                    overflow-y: auto;
                    padding: 0 10px;
                }

                .chat-item {
                    padding: 10px 12px;
                    margin-bottom: 5px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 13.5px;
                    color: #374151;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    transition: background 0.2s;
                }
                .chat-item:hover { background-color: #ececec; }
                .chat-item.active { background-color: #e5e7eb; font-weight: 700; }
                
                .delete-chat-icon {
                    color: #ef4444;
                    font-size: 16px;
                    opacity: 0;
                    transition: opacity 0.2s;
                    cursor: pointer;
                }
                .chat-item:hover .delete-chat-icon { opacity: 1; }

                /* ========================================== */
                /* 💬 بخش اصلی چت (تلگرام) */
                /* ========================================== */
                .main-chat {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    background-color: #e6ebee;
                    background-image: url('https://web.telegram.org/a/chat-bg-pattern-light.ee148af169f9c5c9a46a.png');
                    background-size: cover;
                    background-blend-mode: soft-light;
                    height: 100dvh;
                    position: relative;
                }
                
                .tg-header { 
                    background-color: #ffffff;
                    color: #000000; 
                    padding: 8px 15px; 
                    display: flex; 
                    align-items: center; 
                    border-bottom: 1px solid #e0e0e0;
                    flex-shrink: 0; 
                    z-index: 10;
                }
                
                .menu-btn {
                    display: none; /* در کامپیوتر مخفی است */
                    background: transparent; border: none; font-size: 24px; 
                    color: #707579; cursor: pointer; margin-left: 15px;
                }

                .header-profile { display: flex; align-items: center; }
                .header-avatar { 
                    width: 42px; height: 42px; border-radius: 50%; 
                    background: linear-gradient(135deg, #3390ec, #005bb5); 
                    color: white; display: flex; align-items: center; justify-content: center; 
                    font-size: 22px; margin-left: 12px;
                    box-shadow: 0 2px 5px rgba(51, 144, 236, 0.3);
                }
                .header-info h2 { margin: 0; font-size: 16px; font-weight: 700; }
                .header-info p { margin: 2px 0 0 0; font-size: 13px; color: #707579; }

                .tg-messages { 
                    flex: 1; padding: 20px; overflow-y: auto; 
                    display: flex; flex-direction: column; gap: 8px; 
                }
                
                .message-row { display: flex; align-items: flex-end; width: 100%; }
                .message-row.user { justify-content: flex-start; flex-direction: row-reverse; }
                .message-row.ai { justify-content: flex-start; }
                
                .message-content { max-width: 75%; display: flex; flex-direction: column; }
                
                .message-bubble { 
                    padding: 10px 14px; border-radius: 12px; line-height: 1.6; 
                    font-size: 14.5px; word-wrap: break-word; position: relative;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.08);
                    animation: slideUp 0.3s ease-out forwards;
                }
                
                .message-bubble p { margin: 0 0 8px 0; }
                .message-bubble p:last-child { margin-bottom: 0; }
                .message-bubble strong { font-weight: 700; color: #1a1a1a; }
                .message-bubble ul, .message-bubble ol { margin: 8px 0; padding-right: 20px; }
                .message-bubble li { margin-bottom: 4px; }

                .message-row.user .message-bubble { 
                    background-color: #eeffde; border-top-right-radius: 12px; border-bottom-right-radius: 4px; 
                }
                .message-row.ai .message-bubble { 
                    background-color: #ffffff; border-top-left-radius: 12px; border-bottom-left-radius: 4px; 
                }

                .copy-btn {
                    position: absolute; bottom: -20px; left: 10px;
                    background: transparent; border: none; color: #a2acb4;
                    font-size: 11px; cursor: pointer; opacity: 0; transition: opacity 0.2s;
                }
                .message-row.ai:hover .copy-btn { opacity: 1; }
                .copy-btn:hover { color: #3390ec; }

                .tg-input-area { 
                    display: flex; padding: 8px 15px; padding-bottom: calc(8px + env(safe-area-inset-bottom)); 
                    background-color: #ffffff; align-items: flex-end; box-shadow: 0 -1px 5px rgba(0,0,0,0.05);
                }
                
                .tg-input-area textarea { 
                    flex: 1; padding: 12px 16px; border: 2px solid transparent; background-color: #f4f4f5;
                    border-radius: 18px; outline: none; font-family: inherit; font-size: 14.5px;
                    resize: none; max-height: 120px; line-height: 1.5; overflow-y: auto; color: #000;
                    transition: border 0.3s, background 0.3s;
                }
                .tg-input-area textarea:focus { border-color: #3390ec; background-color: #ffffff; }
                .tg-input-area textarea::placeholder { color: #a2acb4; }
                
                .tg-send-btn { 
                    width: 45px; height: 45px; margin-right: 10px; background: transparent; 
                    color: #3390ec; border: none; border-radius: 50%; cursor: pointer; 
                    display: flex; align-items: center; justify-content: center; transition: background 0.2s, color 0.2s;
                }
                .tg-send-btn:hover { background-color: #f4f4f5; color: #005bb5; }
                .tg-send-btn:disabled { color: #a2acb4; cursor: not-allowed; }

                .typing-indicator { display: flex; gap: 4px; padding: 12px 16px; background: white; border-radius: 12px; border-bottom-left-radius: 4px; width: fit-content; box-shadow: 0 1px 2px rgba(0,0,0,0.08); }
                .typing-indicator span { width: 6px; height: 6px; background-color: #a2acb4; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; }
                .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
                .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
                
                @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
                @keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

                /* ========================================== */
                /* 📱 ریسپانسیو برای موبایل */
                /* ========================================== */
                @media (max-width: 768px) {
                    .sidebar {
                        position: fixed;
                        right: 0; top: 0;
                        transform: translateX(100%); /* مخفی در سمت راست */
                        box-shadow: -2px 0 10px rgba(0,0,0,0.1);
                    }
                    .sidebar.open { transform: translateX(0); }
                    .menu-btn { display: block; }
                    .message-content { max-width: 85%; }
                }
            </style>
        </head>
        <body>
            
            <!-- 🗂️ سایدبار چت‌ها -->
            <div class="sidebar" id="sidebar">
                <button class="new-chat-btn-sidebar" onclick="createNewChat()">
                    <span>+</span> چت جدید
                </button>
                <div class="chat-list" id="chat-list">
                    <!-- لیست چت‌ها با جاوااسکریپت ساخته می‌شود -->
                </div>
            </div>

            <!-- 💬 بخش اصلی چت -->
            <div class="main-chat">
                <div class="tg-header">
                    <button class="menu-btn" onclick="toggleSidebar()">☰</button>
                    <div class="header-profile">
                        <div class="header-avatar">🧠</div>
                        <div class="header-info">
                            <h2>مشاور هوش مصنوعی</h2>
                            <p>متخصص روابط و احساسات</p>
                        </div>
                    </div>
                </div>
                
                <div class="tg-messages" id="chat-box"></div>
                
                <div class="tg-input-area">
                    <textarea id="msg" placeholder="پیام..." rows="1"></textarea>
                    <button class="tg-send-btn" id="send-btn" onclick="send()" title="ارسال">
                        <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path>
                        </svg>
                    </button>
                </div>
            </div>
            
            <script>
                const initialGreeting = "سلام! من اینجا هستم تا در مورد روابط، احساسات و چالش‌هایی که داری با هم صحبت کنیم. امروز چه چیزی ذهن تو را مشغول کرده؟";
                const chatBox = document.getElementById('chat-box');
                const msgInput = document.getElementById('msg');
                const chatListDiv = document.getElementById('chat-list');
                const sidebar = document.getElementById('sidebar');

                // داده‌های اصلی برنامه
                let allChats = [];
                let currentChatId = null;

                // ۱. لود کردن اطلاعات از حافظه مرورگر
                function initApp() {
                    const savedData = localStorage.getItem('aiCounselorData');
                    if (savedData) {
                        const parsed = JSON.parse(savedData);
                        allChats = parsed.chats || [];
                        currentChatId = parsed.currentChatId;
                    }
                    
                    // اگر هیچ چتی وجود نداشت، یکی بساز
                    if (allChats.length === 0) {
                        createNewChat();
                    } else {
                        // اگر چت فعلی پیدا نشد، اولین چت را باز کن
                        if (!currentChatId || !allChats.find(c => c.id === currentChatId)) {
                            currentChatId = allChats[0].id;
                        }
                        loadChat(currentChatId);
                    }
                }

                // ۲. ذخیره کل داده‌ها در حافظه
                function saveData() {
                    localStorage.setItem('aiCounselorData', JSON.stringify({
                        chats: allChats,
                        currentChatId: currentChatId
                    }));
                }

                // ۳. رندر کردن لیست چت‌ها در سایدبار
                function renderSidebar() {
                    chatListDiv.innerHTML = '';
                    // مرتب‌سازی چت‌ها از جدیدترین به قدیمی‌ترین
                    allChats.sort((a, b) => b.timestamp - a.timestamp);
                    
                    allChats.forEach(chat => {
                        const item = document.createElement('div');
                        item.className = `chat-item ${chat.id === currentChatId ? 'active' : ''}`;
                        
                        const titleSpan = document.createElement('span');
                        titleSpan.innerText = chat.title;
                        
                        const deleteBtn = document.createElement('span');
                        deleteBtn.className = 'delete-chat-icon';
                        deleteBtn.innerText = '✕';
                        deleteBtn.title = "حذف چت";
                        deleteBtn.onclick = (e) => {
                            e.stopPropagation(); // جلوگیری از باز شدن چت
                            deleteChat(chat.id);
                        };

                        item.appendChild(titleSpan);
                        item.appendChild(deleteBtn);
                        
                        item.onclick = () => {
                            loadChat(chat.id);
                            if (window.innerWidth <= 768) toggleSidebar(); // بستن منو در موبایل
                        };
                        
                        chatListDiv.appendChild(item);
                    });
                }

                // ۴. ایجاد چت جدید
                function createNewChat() {
                    const newId = 'chat_' + Date.now();
                    const newChat = {
                        id: newId,
                        title: "گفتگوی جدید",
                        messages: [{ role: 'assistant', content: initialGreeting }],
                        timestamp: Date.now()
                    };
                    
                    allChats.unshift(newChat); // اضافه به اول لیست
                    currentChatId = newId;
                    
                    saveData();
                    renderSidebar();
                    loadChat(newId);
                    
                    if (window.innerWidth <= 768 && sidebar.classList.contains('open')) {
                        toggleSidebar();
                    }
                }

                // ۵. لود کردن یک چت خاص
                function loadChat(chatId) {
                    currentChatId = chatId;
                    const chat = allChats.find(c => c.id === chatId);
                    if (!chat) return;

                    chatBox.innerHTML = ''; // پاک کردن صفحه
                    
                    chat.messages.forEach(msg => {
                        appendMessageUI(msg.role === 'user' ? 'user' : 'ai', msg.content, false);
                    });
                    
                    chatBox.scrollTop = chatBox.scrollHeight;
                    renderSidebar();
                    saveData();
                }

                // ۶. حذف چت
                function deleteChat(chatId) {
                    if (confirm("این گفتگو حذف شود؟")) {
                        allChats = allChats.filter(c => c.id !== chatId);
                        
                        // اگر چتی که حذف شد، چت فعلی بود
                        if (currentChatId === chatId) {
                            if (allChats.length > 0) {
                                currentChatId = allChats[0].id;
                                loadChat(currentChatId);
                            } else {
                                createNewChat(); // اگر همه چت‌ها حذف شدند، یکی جدید بساز
                            }
                        } else {
                            saveData();
                            renderSidebar();
                        }
                    }
                }

                // ۷. باز و بسته کردن منو در موبایل
                function toggleSidebar() {
                    sidebar.classList.toggle('open');
                }

                // ۸. تنظیم ارتفاع کادر تایپ
                msgInput.addEventListener('input', function() {
                    this.style.height = 'auto';
                    this.style.height = (this.scrollHeight) + 'px';
                    if(this.value === '') this.style.height = 'auto';
                });

                // ۹. ارسال پیام
                async function send() {
                    const msg = msgInput.value.trim();
                    if (!msg || !currentChatId) return;

                    msgInput.style.height = 'auto';
                    msgInput.value = '';
                    
                    let currentChat = allChats.find(c => c.id === currentChatId);
                    
                    // آپدیت UI
                    appendMessageUI('user', msg);
                    
                    // آپدیت دیتا
                    currentChat.messages.push({ role: 'user', content: msg });
                    
                    // اگر این اولین پیام کاربر بود، عنوان چت را تغییر بده
                    if (currentChat.messages.length === 2 && currentChat.title === "گفتگوی جدید") {
                        currentChat.title = msg.substring(0, 25) + (msg.length > 25 ? '...' : '');
                    }
                    
                    currentChat.timestamp = Date.now();
                    saveData();
                    renderSidebar();

                    // ارسال به API (فقط ۱۲ پیام آخر برای ذخیره توکن)
                    const apiMessages = currentChat.messages.slice(-12);
                    
                    const typingId = showTypingIndicator();
                    const sendBtn = document.getElementById('send-btn');
                    sendBtn.disabled = true;
                    
                    try {
                        const res = await fetch('/chat', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ messages: apiMessages })
                        });
                        const data = await res.json();
                        const reply = data.reply || data.detail || "خطای نامشخص";

                        removeTypingIndicator(typingId);
                        appendMessageUI('ai', reply);
                        
                        // آپدیت دیتا با پاسخ هوش مصنوعی
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

                // ۱۰. ساخت المان پیام در صفحه
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
                        copyBtn.innerText = 'کپی 📋';
                        copyBtn.onclick = () => {
                            navigator.clipboard.writeText(text);
                            copyBtn.innerText = 'کپی شد! ✓';
                            setTimeout(() => copyBtn.innerText = 'کپی 📋', 2000);
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

                // شروع برنامه
                window.onload = initApp;
            </script>
        </body>
    </html>
    """
