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
# 🎯 بخش تنظیمات پرامپت (شخصیت و قوانین ربات)
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
    
    system_message = {
        "role": "system", 
        "content": SYSTEM_PROMPT
    }
    
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
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;700&display=swap');
                
                html, body { height: 100%; margin: 0; padding: 0; overflow: hidden; background-color: #e6ebee; }
                
                body { 
                    font-family: 'Vazirmatn', Tahoma, sans-serif; 
                    display: flex; 
                    justify-content: center; 
                    align-items: center; 
                }
                
                /* بدنه اصلی برنامه */
                .tg-container { 
                    width: 100%; 
                    height: 100dvh; 
                    display: flex; 
                    flex-direction: column; 
                    background-color: #e6ebee;
                    /* پترن پس‌زمینه شبیه تلگرام */
                    background-image: url('https://web.telegram.org/a/chat-bg-pattern-light.ee148af169f9c5c9a46a.png');
                    background-size: cover;
                    background-blend-mode: soft-light;
                }
                
                /* هدر تلگرام */
                .tg-header { 
                    background-color: #ffffff;
                    color: #000000; 
                    padding: 8px 15px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: space-between;
                    border-bottom: 1px solid #e0e0e0;
                    flex-shrink: 0; 
                    z-index: 10;
                    cursor: pointer;
                }
                .tg-header:hover { background-color: #f4f4f5; }
                
                .header-profile { display: flex; align-items: center; }
                .header-avatar { 
                    width: 42px; height: 42px; border-radius: 50%; 
                    background: linear-gradient(135deg, #3390ec, #005bb5); 
                    color: white; display: flex; align-items: center; justify-content: center; 
                    font-size: 22px; margin-left: 12px;
                }
                .header-info h2 { margin: 0; font-size: 16px; font-weight: 500; }
                .header-info p { margin: 2px 0 0 0; font-size: 13px; color: #707579; }

                .new-chat-btn {
                    background: transparent; border: none; color: #707579;
                    font-size: 20px; cursor: pointer; padding: 8px;
                    border-radius: 50%; transition: background 0.2s;
                }
                .new-chat-btn:hover { background: #f4f4f5; }

                /* ناحیه پیام‌ها */
                .tg-messages { 
                    flex: 1; 
                    padding: 20px 20px; 
                    overflow-y: auto; 
                    display: flex; 
                    flex-direction: column; 
                    gap: 8px; 
                }
                
                .message-row { display: flex; align-items: flex-end; width: 100%; }
                /* پیام‌های شما در سمت چپ (استاندارد تلگرام فارسی) */
                .message-row.user { justify-content: flex-start; flex-direction: row-reverse; }
                /* پیام‌های هوش مصنوعی در سمت راست */
                .message-row.ai { justify-content: flex-start; }
                
                .avatar { display: none; } /* در تلگرام آواتار داخل چت نشان داده نمی‌شود */
                
                .message-content { max-width: 75%; display: flex; flex-direction: column; }
                
                /* حباب‌های گفتگو */
                .message-bubble { 
                    padding: 8px 12px; 
                    border-radius: 12px; 
                    line-height: 1.5; 
                    font-size: 14.5px; 
                    word-wrap: break-word; 
                    position: relative;
                    box-shadow: 0 1px 1px rgba(0,0,0,0.1);
                }
                
                /* حباب پیام کاربر (سبز روشن تلگرام) */
                .message-row.user .message-bubble { 
                    background-color: #eeffde; 
                    border-top-right-radius: 12px;
                    border-bottom-right-radius: 4px; /* گوشه تیز */
                }
                
                /* حباب پیام هوش مصنوعی (سفید) */
                .message-row.ai .message-bubble { 
                    background-color: #ffffff; 
                    border-top-left-radius: 12px;
                    border-bottom-left-radius: 4px; /* گوشه تیز */
                }

                /* ناحیه تایپ کردن */
                .tg-input-area { 
                    display: flex; 
                    padding: 8px 15px; 
                    padding-bottom: calc(8px + env(safe-area-inset-bottom)); 
                    background-color: #ffffff; 
                    align-items: flex-end; 
                    box-shadow: 0 -1px 2px rgba(0,0,0,0.05);
                }
                
                .tg-input-area textarea { 
                    flex: 1; 
                    padding: 12px 16px; 
                    border: none; 
                    background-color: #f4f4f5;
                    border-radius: 18px; 
                    outline: none; 
                    font-family: inherit; 
                    font-size: 14.5px;
                    resize: none; 
                    max-height: 120px; 
                    line-height: 1.5;
                    overflow-y: auto;
                    color: #000;
                }
                .tg-input-area textarea::placeholder { color: #a2acb4; }
                
                /* دکمه ارسال تلگرام (آیکون کاغذ) */
                .tg-send-btn { 
                    width: 45px;
                    height: 45px;
                    margin-right: 10px; 
                    background: transparent; 
                    color: #3390ec; 
                    border: none; 
                    border-radius: 50%; 
                    cursor: pointer; 
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: background 0.2s;
                }
                .tg-send-btn:hover { background-color: #f4f4f5; }
                .tg-send-btn:disabled { color: #a2acb4; cursor: not-allowed; }

                /* انیمیشن تایپ */
                .typing-indicator { display: flex; gap: 4px; padding: 12px 16px; background: white; border-radius: 12px; border-bottom-left-radius: 4px; width: fit-content; box-shadow: 0 1px 1px rgba(0,0,0,0.1); }
                .typing-indicator span { width: 6px; height: 6px; background-color: #a2acb4; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; }
                .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
                .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
                @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

                /* ========================================== */
                /* 🖥️ تنظیمات دسکتاپ (شبیه تلگرام وب) */
                /* ========================================== */
                @media (min-width: 768px) {
                    .tg-container { 
                        max-width: 900px; 
                        height: 95dvh; 
                        border-radius: 10px; 
                        box-shadow: 0 10px 40px rgba(0,0,0,0.15); 
                        border: 1px solid rgba(0,0,0,0.1);
                    }
                    .tg-header { border-top-left-radius: 10px; border-top-right-radius: 10px; }
                    .tg-input-area { border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; }
                    .message-content { max-width: 65%; }
                }
            </style>
        </head>
        <body>
            <div class="tg-container">
                
                <!-- هدر تلگرام -->
                <div class="tg-header">
                    <div class="header-profile">
                        <div class="header-avatar">🧠</div>
                        <div class="header-info">
                            <h2>مشاور هوش مصنوعی</h2>
                            <p>متخصص روابط و احساسات</p>
                        </div>
                    </div>
                    <button class="new-chat-btn" onclick="startNewChat()" title="پاک کردن تاریخچه">🗑️</button>
                </div>
                
                <!-- محیط چت -->
                <div class="tg-messages" id="chat-box">
                    <!-- پیام‌ها با جاوااسکریپت لود می‌شوند -->
                </div>
                
                <!-- کادر ارسال پیام -->
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
                let chatHistory = []; 
                const chatBox = document.getElementById('chat-box');
                const msgInput = document.getElementById('msg');

                function loadChat() {
                    const savedChat = localStorage.getItem('aiCounselorChat');
                    if (savedChat) {
                        chatHistory = JSON.parse(savedChat);
                        chatHistory.forEach(msg => appendMessageUI(msg.role === 'user' ? 'user' : 'ai', msg.content));
                    } else {
                        appendMessageUI('ai', initialGreeting);
                    }
                    chatBox.scrollTop = chatBox.scrollHeight;
                }

                function saveChat() {
                    localStorage.setItem('aiCounselorChat', JSON.stringify(chatHistory));
                }

                function startNewChat() {
                    if (confirm("آیا مطمئن هستید که می‌خواهید تاریخچه این گفتگو را پاک کنید؟")) {
                        chatHistory = [];
                        localStorage.removeItem('aiCounselorChat');
                        chatBox.innerHTML = '';
                        appendMessageUI('ai', initialGreeting);
                    }
                }

                msgInput.addEventListener('input', function() {
                    this.style.height = 'auto';
                    this.style.height = (this.scrollHeight) + 'px';
                    if(this.value === '') this.style.height = 'auto';
                });

                async function send() {
                    const msg = msgInput.value.trim();
                    if (!msg) return;

                    msgInput.style.height = 'auto';

                    appendMessageUI('user', msg);
                    msgInput.value = '';
                    
                    chatHistory.push({ role: 'user', content: msg });
                    saveChat(); 

                    if (chatHistory.length > 12) {
                        chatHistory = chatHistory.slice(chatHistory.length - 12);
                        saveChat();
                    }

                    const typingId = showTypingIndicator();
                    const sendBtn = document.getElementById('send-btn');
                    sendBtn.disabled = true;
                    
                    try {
                        const res = await fetch('/chat', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ messages: chatHistory })
                        });
                        const data = await res.json();
                        const reply = data.reply || data.detail || "خطای نامشخص";

                        removeTypingIndicator(typingId);
                        appendMessageUI('ai', reply);
                        
                        chatHistory.push({ role: 'assistant', content: reply });
                        saveChat(); 

                        if (chatHistory.length > 12) {
                            chatHistory = chatHistory.slice(chatHistory.length - 12);
                            saveChat();
                        }

                    } catch(e) {
                        removeTypingIndicator(typingId);
                        appendMessageUI('ai', "ارتباط برقرار نشد. دوباره تلاش کنید.");
                        chatHistory.pop(); 
                    } finally {
                        sendBtn.disabled = false;
                    }
                }

                function appendMessageUI(role, text) {
                    if (!text || !text.trim()) return; 

                    const row = document.createElement('div');
                    row.className = `message-row ${role}`;
                    
                    const content = document.createElement('div');
                    content.className = 'message-content';
                    
                    const bubble = document.createElement('div');
                    bubble.className = 'message-bubble';
                    bubble.innerText = text;
                    
                    content.appendChild(bubble);
                    row.appendChild(content);
                    
                    chatBox.appendChild(row);
                    chatBox.scrollTop = chatBox.scrollHeight; 
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

                window.onload = loadChat;
            </script>
        </body>
    </html>
    """
