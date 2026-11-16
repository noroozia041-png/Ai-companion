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

# =========================================================================
# 🎯 پرامپت فوق تخصصی (Prompt Engineering) برای «مرهم»
# این دستورالعمل به هوش مصنوعی یاد می‌دهد که مثل یک روانشناس واقعی عمل کند
# =========================================================================
SYSTEM_PROMPT = """
[نقش و هویت]
تو «مرهم» هستی؛ یک مشاور متخصص و بسیار همدل در حوزه روابط (خانوادگی، عاطفی و بین‌فردی). 
رویکرد تو ترکیبی از درمان شناختی-رفتاری (CBT) و مدل ارتباط بدون خشونت (NVC) است.
لحن تو آرام، امن، بدون قضاوت و مثل یک دوست بسیار دانا و حرفه‌ای است.

[پروتکل پاسخ‌دهی - در هر پیام این ۴ مرحله را طی کن]
۱. اعتباربخشی (Validation): ابتدا احساس کاربر را با یک جمله کوتاه تایید کن (مثلاً: «کاملاً درک می‌کنم که این شرایط چقدر می‌تواند خسته‌کننده باشد»). هرگز سریع نصیحت نکن.
۲. کشف افکار (Exploration): سعی کن پشت احساسات کاربر (مثل عصبانیت یا نفرت)، «نیاز» یا «فکر منفی» پنهان را پیدا کنی.
۳. ارائه ابزار (Tool): یک تکنیک عملی، کوتاه و قابل اجرا به کاربر بده (مثلاً نحوه بیان یک درخواست با جملات «من» در NVC).
۴. سوال پایانی (Call to Action): مکالمه را با یک سوال باز (Open-ended) به جلو ببر. پاسخ شما هرگز نباید بدون سوال تمام شود.

[قوانین سخت‌گیرانه]
- پاسخ‌ها باید حداکثر ۱۵۰ کلمه باشند. از نوشتن متن‌های طولانی و پشت سر هم خودداری کن.
- هرگز طرف مقابل (مثل همسر، خواهر، پدر و مادر) را قضاوت نکن. فقط روی «الگوهای ارتباطی» تمرکز کن.
- از کلمات تخصصی و پیچیده روانشناسی استفاده نکن؛ ساده و محاوره‌ای صحبت کن.
- اگر کاربر نشانه‌هایی از خودکشی، خودآسیبی یا آزار و اذیت شدید نشان داد، فوراً تمام تکنیک‌ها را متوقف کن و با لحنی دلسوزانه، او را به اورژانس اجتماعی (۱۲۳) یا خط صدای مشاور (۱۴۸۰) ارجاع بده.
"""
# =========================================================================

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
        "temperature": 0.7 # دمای متعادل برای حفظ خلاقیت و دقت
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
            <title>مرهم | همراه و مشاور شما</title>
            <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700&display=swap');
                
                :root {
                    --bg-body: #f0f2f5;
                    --sidebar-bg: #ffffff;
                    --chat-bg: #f7f9fc;
                    --primary: #4f46e5; 
                    --primary-hover: #4338ca;
                    --text-main: #1f2937;
                    --text-muted: #6b7280;
                    --user-bubble: #e0e7ff; 
                    --ai-bubble: #ffffff;
                    --border-color: #e5e7eb;
                }
                
                html, body { height: 100%; margin: 0; padding: 0; overflow: hidden; background-color: var(--bg-body); }
                
                body { font-family: 'Vazirmatn', Tahoma, sans-serif; display: flex; color: var(--text-main); }
                
                ::-webkit-scrollbar { width: 6px; }
                ::-webkit-scrollbar-track { background: transparent; }
                ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
                ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

                .sidebar {
                    width: 280px; background-color: var(--sidebar-bg);
                    border-left: 1px solid var(--border-color);
                    display: flex; flex-direction: column; height: 100dvh;
                    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    z-index: 100; box-shadow: 2px 0 10px rgba(0,0,0,0.02);
                }
                
                .sidebar-header { padding: 20px 20px 10px 20px; font-weight: 700; font-size: 18px; color: var(--primary); display: flex; align-items: center; gap: 8px; }

                .new-chat-btn-sidebar {
                    margin: 0 15px 15px 15px; padding: 12px; background-color: var(--primary);
                    border: none; border-radius: 12px; font-family: inherit; font-size: 14px;
                    font-weight: 500; color: #ffffff; cursor: pointer;
                    display: flex; align-items: center; justify-content: center; gap: 8px;
                    transition: background 0.2s, transform 0.1s; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
                }
                .new-chat-btn-sidebar:hover { background-color: var(--primary-hover); }
                .new-chat-btn-sidebar:active { transform: scale(0.98); }

                .chat-list { flex: 1; overflow-y: auto; padding: 0 10px; }

                .chat-item {
                    padding: 12px; margin-bottom: 4px; border-radius: 10px; cursor: pointer;
                    font-size: 14px; color: var(--text-main); white-space: nowrap; overflow: hidden;
                    text-overflow: ellipsis; display: flex; justify-content: space-between;
                    align-items: center; transition: all 0.2s ease;
                }
                .chat-item:hover { background-color: #f3f4f6; }
                .chat-item.active { background-color: #f3f4f6; font-weight: 700; color: var(--primary); }
                
                .delete-chat-icon { color: #ef4444; font-size: 14px; opacity: 0; transition: opacity 0.2s; padding: 4px; }
                .chat-item:hover .delete-chat-icon { opacity: 1; }

                .main-chat {
                    flex: 1; display: flex; flex-direction: column; background-color: var(--chat-bg);
                    background-image: radial-gradient(#e5e7eb 1px, transparent 1px); background-size: 20px 20px;
                    height: 100dvh; position: relative;
                }
                
                .tg-header { 
                    background-color: rgba(255, 255, 255, 0.85); backdrop-filter: blur(10px);
                    -webkit-backdrop-filter: blur(10px); color: var(--text-main); padding: 12px 20px; 
                    display: flex; align-items: center; border-bottom: 1px solid var(--border-color);
                    flex-shrink: 0; z-index: 10;
                }
                
                .menu-btn { display: none; background: transparent; border: none; font-size: 24px; color: var(--text-muted); cursor: pointer; margin-left: 15px; }

                .header-profile { display: flex; align-items: center; }
                .header-avatar { 
                    width: 46px; height: 46px; border-radius: 50%; background: linear-gradient(135deg, #818cf8, #4f46e5); 
                    color: white; display: flex; align-items: center; justify-content: center; 
                    font-size: 24px; margin-left: 15px; box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3); position: relative;
                }
                .header-avatar::after {
                    content: ''; position: absolute; width: 100%; height: 100%; border-radius: 50%;
                    border: 2px solid #818cf8; animation: pulse 2s infinite; opacity: 0;
                }
                @keyframes pulse { 0% { transform: scale(1); opacity: 0.5; } 100% { transform: scale(1.3); opacity: 0; } }

                .header-info h2 { margin: 0; font-size: 18px; font-weight: 700; color: var(--primary); }
                .header-info p { margin: 4px 0 0 0; font-size: 13px; color: var(--text-muted); }

                .tg-messages { flex: 1; padding: 25px 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; }
                
                .message-row { display: flex; align-items: flex-end; width: 100%; }
                .message-row.user { justify-content: flex-start; flex-direction: row-reverse; }
                .message-row.ai { justify-content: flex-start; }
                
                .message-content { max-width: 75%; display: flex; flex-direction: column; }
                
                .message-bubble { 
                    padding: 14px 18px; border-radius: 18px; line-height: 1.7; font-size: 15px; 
                    word-wrap: break-word; position: relative; animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
                }
                
                .message-bubble p { margin: 0 0 10px 0; }
                .message-bubble p:last-child { margin-bottom: 0; }
                .message-bubble strong { font-weight: 700; color: var(--primary); }
                .message-bubble ul, .message-bubble ol { margin: 10px 0; padding-right: 24px; }
                .message-bubble li { margin-bottom: 6px; }

                .message-row.user .message-bubble { 
                    background-color: var(--user-bubble); color: #1e1b4b; border-top-right-radius: 4px; 
                    border-bottom-left-radius: 18px; border-bottom-right-radius: 18px;
                    box-shadow: 0 2px 8px rgba(224, 231, 255, 0.5);
                }
                
                .message-row.ai .message-bubble { 
                    background-color: var(--ai-bubble); border: 1px solid var(--border-color);
                    border-top-left-radius: 4px; border-bottom-left-radius: 18px; border-bottom-right-radius: 18px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.03);
                    padding-bottom: 25px; /* فضای خالی برای دکمه کپی */
                }

                /* 🎨 دکمه کپی بازطراحی شده */
                .copy-btn {
                    position: absolute;
                    bottom: 6px;
                    left: 8px; /* در حالت RTL سمت چپ پایین قرار می‌گیرد */
                    background: transparent;
                    border: none;
                    color: #9ca3af;
                    cursor: pointer;
                    opacity: 0;
                    transition: all 0.2s ease;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 4px;
                    border-radius: 6px;
                }
                
                .copy-btn svg {
                    width: 14px;
                    height: 14px;
                    fill: currentColor;
                }

                .message-row.ai:hover .copy-btn { opacity: 1; }
                .copy-btn:hover { color: var(--primary); background-color: #f3f4f6; }
                .copy-btn.copied { color: #10b981; } /* رنگ سبز برای تایید کپی */

                .input-wrapper { padding: 10px 20px 20px 20px; background: linear-gradient(to top, var(--chat-bg) 70%, transparent); }

                .tg-input-area { 
                    display: flex; padding: 6px 10px; background-color: #ffffff; align-items: flex-end; 
                    border-radius: 24px; box-shadow: 0 5px 20px rgba(0,0,0,0.06); border: 1px solid var(--border-color);
                    transition: border-color 0.3s, box-shadow 0.3s;
                }
                .tg-input-area:focus-within { border-color: #a5b4fc; box-shadow: 0 5px 25px rgba(79, 70, 229, 0.1); }
                
                .tg-input-area textarea { 
                    flex: 1; padding: 12px 16px; border: none; background-color: transparent;
                    border-radius: 18px; outline: none; font-family: inherit; font-size: 15px;
                    resize: none; max-height: 150px; line-height: 1.5; overflow-y: auto; color: var(--text-main);
                }
                .tg-input-area textarea::placeholder { color: #9ca3af; }
                
                .tg-send-btn { 
                    width: 44px; height: 44px; margin: 2px; background: linear-gradient(135deg, #6366f1, #4f46e5); 
                    color: white; border: none; border-radius: 50%; cursor: pointer; 
                    display: flex; align-items: center; justify-content: center; 
                    transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3); flex-shrink: 0;
                }
                .tg-send-btn:hover { transform: scale(1.05); box-shadow: 0 6px 15px rgba(79, 70, 229, 0.4); }
                .tg-send-btn:disabled { background: #e5e7eb; color: #9ca3af; box-shadow: none; cursor: not-allowed; transform: none; }

                .typing-indicator { display: flex; gap: 5px; padding: 16px 20px; background: var(--ai-bubble); border: 1px solid var(--border-color); border-radius: 18px; border-top-left-radius: 4px; width: fit-content; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
                .typing-indicator span { width: 6px; height: 6px; background-color: #a5b4fc; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; }
                .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
                .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
                
                @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
                @keyframes slideUp { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }

                @media (max-width: 768px) {
                    .sidebar { position: fixed; right: 0; top: 0; transform: translateX(100%); box-shadow: -5px 0 25px rgba(0,0,0,0.1); }
                    .sidebar.open { transform: translateX(0); }
                    .menu-btn { display: block; }
                    .message-content { max-width: 88%; }
                    .input-wrapper { padding: 10px 15px 15px 15px; }
                }
            </style>
        </head>
        <body>
            
            <div class="sidebar" id="sidebar">
                <div class="sidebar-header"><span>🍃</span> مرهم</div>
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
                            <p>همراه و مشاور شما در روابط</p>
                        </div>
                    </div>
                </div>
                
                <div class="tg-messages" id="chat-box"></div>
                
                <div class="input-wrapper">
                    <div class="tg-input-area">
                        <textarea id="msg" placeholder="هر چیزی که در ذهنت هست را بنویس..." rows="1"></textarea>
                        <button class="tg-send-btn" id="send-btn" onclick="send()" title="ارسال">
                            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
            
            <script>
                const initialGreeting = "سلام! من «مرهم» هستم. اینجا هستم تا در مورد روابط، احساسات و چالش‌هایی که داری با هم صحبت کنیم. امروز چه چیزی ذهن تو را مشغول کرده؟";
                const chatBox = document.getElementById('chat-box');
                const msgInput = document.getElementById('msg');
                const chatListDiv = document.getElementById('chat-list');
                const sidebar = document.getElementById('sidebar');

                let allChats = [];
                let currentChatId = null;

                function initApp() {
                    const savedData = localStorage.getItem('marhamAppData');
                    if (savedData) {
                        const parsed = JSON.parse(savedData);
                        allChats = parsed.chats || [];
                        currentChatId = parsed.currentChatId;
                    }
                    if (allChats.length === 0) { createNewChat(); } 
                    else {
                        if (!currentChatId || !allChats.find(c => c.id === currentChatId)) currentChatId = allChats[0].id;
                        loadChat(currentChatId);
                    }
                }

                function saveData() {
                    localStorage.setItem('marhamAppData', JSON.stringify({ chats: allChats, currentChatId: currentChatId }));
                }

                function renderSidebar() {
                    chatListDiv.innerHTML = '';
                    allChats.sort((a, b) => b.timestamp - a.timestamp);
                    allChats.forEach(chat => {
                        const item = document.createElement('div');
                        item.className = `chat-item ${chat.id === currentChatId ? 'active' : ''}`;
                        const titleSpan = document.createElement('span'); titleSpan.innerText = chat.title;
                        const deleteBtn = document.createElement('span'); deleteBtn.className = 'delete-chat-icon'; deleteBtn.innerText = '✕';
                        deleteBtn.onclick = (e) => { e.stopPropagation(); deleteChat(chat.id); };
                        item.appendChild(titleSpan); item.appendChild(deleteBtn);
                        item.onclick = () => { loadChat(chat.id); if (window.innerWidth <= 768) toggleSidebar(); };
                        chatListDiv.appendChild(item);
                    });
                }

                function createNewChat() {
                    const newId = 'chat_' + Date.now();
                    const newChat = { id: newId, title: "گفتگوی جدید", messages: [{ role: 'assistant', content: initialGreeting }], timestamp: Date.now() };
                    allChats.unshift(newChat); currentChatId = newId;
                    saveData(); renderSidebar(); loadChat(newId);
                    if (window.innerWidth <= 768 && sidebar.classList.contains('open')) toggleSidebar();
                }

                function loadChat(chatId) {
                    currentChatId = chatId;
                    const chat = allChats.find(c => c.id === chatId);
                    if (!chat) return;
                    chatBox.innerHTML = '';
                    chat.messages.forEach(msg => appendMessageUI(msg.role === 'user' ? 'user' : 'ai', msg.content, false));
                    chatBox.scrollTop = chatBox.scrollHeight;
                    renderSidebar(); saveData();
                }

                function deleteChat(chatId) {
                    if (confirm("این گفتگو برای همیشه حذف شود؟")) {
                        allChats = allChats.filter(c => c.id !== chatId);
                        if (currentChatId === chatId) {
                            if (allChats.length > 0) { currentChatId = allChats[0].id; loadChat(currentChatId); } 
                            else { createNewChat(); }
                        } else { saveData(); renderSidebar(); }
                    }
                }

                function toggleSidebar() { sidebar.classList.toggle('open'); }

                msgInput.addEventListener('input', function() {
                    this.style.height = 'auto';
                    this.style.height = (this.scrollHeight) + 'px';
                    if(this.value === '') this.style.height = 'auto';
                });

                async function send() {
                    const msg = msgInput.value.trim();
                    if (!msg || !currentChatId) return;
                    msgInput.style.height = 'auto'; msgInput.value = '';
                    
                    let currentChat = allChats.find(c => c.id === currentChatId);
                    appendMessageUI('user', msg);
                    currentChat.messages.push({ role: 'user', content: msg });
                    
                    if (currentChat.messages.length === 2 && currentChat.title === "گفتگوی جدید") {
                        currentChat.title = msg.substring(0, 25) + (msg.length > 25 ? '...' : '');
                    }
                    currentChat.timestamp = Date.now(); saveData(); renderSidebar();

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
                        
                        currentChat.messages.push({ role: 'assistant', content: reply });
                        currentChat.timestamp = Date.now(); saveData();
                    } catch(e) {
                        removeTypingIndicator(typingId);
                        appendMessageUI('ai', "ارتباط برقرار نشد. دوباره تلاش کنید.");
                    } finally { sendBtn.disabled = false; }
                }

                function appendMessageUI(role, text, scroll = true) {
                    if (!text || !text.trim()) return; 
                    const row = document.createElement('div'); row.className = `message-row ${role}`;
                    const content = document.createElement('div'); content.className = 'message-content';
                    const bubble = document.createElement('div'); bubble.className = 'message-bubble';
                    
                    if (role === 'ai') {
                        bubble.innerHTML = marked.parse(text);
                        // 🎨 دکمه کپی با آیکون SVG
                        const copyBtn = document.createElement('button');
                        copyBtn.className = 'copy-btn';
                        copyBtn.title = "کپی متن";
                        copyBtn.innerHTML = `<svg viewBox="0 0 24 24"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>`;
                        
                        copyBtn.onclick = () => {
                            navigator.clipboard.writeText(text);
                            copyBtn.classList.add('copied');
                            // تغییر آیکون به تیک سبز
                            copyBtn.innerHTML = `<svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>`;
                            setTimeout(() => {
                                copyBtn.classList.remove('copied');
                                copyBtn.innerHTML = `<svg viewBox="0 0 24 24"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>`;
                            }, 2000);
                        };
                        bubble.appendChild(copyBtn);
                    } else {
                        bubble.innerText = text;
                    }
                    
                    content.appendChild(bubble); row.appendChild(content); chatBox.appendChild(row);
                    if (scroll) chatBox.scrollTop = chatBox.scrollHeight; 
                }

                function showTypingIndicator() {
                    const id = 'typing-' + Date.now();
                    const row = document.createElement('div'); row.className = 'message-row ai'; row.id = id;
                    const content = document.createElement('div'); content.className = 'message-content';
                    const typing = document.createElement('div'); typing.className = 'typing-indicator';
                    typing.innerHTML = '<span></span><span></span><span></span>';
                    content.appendChild(typing); row.appendChild(content);
                    chatBox.appendChild(row); chatBox.scrollTop = chatBox.scrollHeight;
                    return id;
                }

                function removeTypingIndicator(id) {
                    const el = document.getElementById(id);
                    if (el) el.remove();
                }

                window.onload = initApp;
            </script>
        </body>
    </html>
    """
