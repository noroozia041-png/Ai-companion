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
# هر تغییری که در رفتار ربات می‌خواهید، فقط همین متن زیر را تغییر دهید.
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
    
    # استفاده از پرامپت تعریف شده در بالای فایل
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
                @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
                
                html, body { height: 100%; margin: 0; padding: 0; overflow: hidden; }
                
                body { 
                    font-family: 'Vazirmatn', Tahoma, sans-serif; 
                    background-color: #e5ddd5; 
                    display: flex; 
                    justify-content: center; 
                    align-items: center; /* برای وسط چین کردن در دسکتاپ */
                }
                
                /* ظاهر پیش‌فرض (موبایل) */
                .chat-container { 
                    width: 100%; 
                    max-width: 100%; 
                    background: #efeae2; 
                    display: flex; 
                    flex-direction: column; 
                    height: 100dvh; /* پر کردن کل صفحه در موبایل */
                    overflow: hidden;
                }
                
                .chat-header { 
                    background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                    color: white; 
                    padding: 10px 15px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: space-between;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    flex-shrink: 0; 
                    z-index: 10;
                }
                .header-profile { display: flex; align-items: center; }
                .header-info { margin-right: 15px; }
                .header-info h2 { margin: 0; font-size: 18px; }
                .header-info p { margin: 0; font-size: 12px; color: #b0c4de; }
                .online-dot { height: 10px; width: 10px; background-color: #25d366; border-radius: 50%; display: inline-block; margin-left: 5px; }

                .new-chat-btn {
                    background: rgba(255, 255, 255, 0.2);
                    border: none;
                    color: white;
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    font-size: 20px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: background 0.3s;
                }
                .new-chat-btn:hover { background: rgba(255, 255, 255, 0.4); }

                .chat-messages { 
                    flex: 1; 
                    padding: 20px 15px; 
                    overflow-y: auto; 
                    display: flex; 
                    flex-direction: column; 
                    gap: 15px; 
                    background-image: url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png');
                    background-blend-mode: overlay;
                }
                
                .message-row { display: flex; align-items: flex-end; width: 100%; }
                .message-row.user { justify-content: flex-start; flex-direction: row-reverse; }
                .message-row.ai { justify-content: flex-start; }
                
                .avatar { width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
                .avatar.user { background: #007bff; color: white; margin-left: 10px; }
                .avatar.ai { background: #e67e22; color: white; margin-right: 10px; }

                .message-content { max-width: 80%; display: flex; flex-direction: column; }
                .message-row.user .message-content { align-items: flex-end; }
                .message-row.ai .message-content { align-items: flex-start; }
                
                .sender-name { font-size: 11px; color: #666; margin-bottom: 3px; margin-right: 5px; margin-left: 5px;}
                
                .message-bubble { 
                    padding: 12px 16px; 
                    border-radius: 15px; 
                    line-height: 1.6; 
                    font-size: 14px; 
                    word-wrap: break-word; 
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                    position: relative;
                }
                .message-row.user .message-bubble { background: #dcf8c6; border-top-right-radius: 0; }
                .message-row.ai .message-bubble { background: white; border-top-left-radius: 0; }

                .chat-input-area { 
                    display: flex; 
                    padding: 10px 12px; 
                    padding-bottom: calc(10px + env(safe-area-inset-bottom)); 
                    background: #f0f0f0; 
                    border-top: 1px solid #ddd; 
                    flex-shrink: 0;
                    align-items: flex-end; 
                }
                
                .chat-input-area textarea { 
                    flex: 1; 
                    padding: 12px 15px; 
                    border: none; 
                    border-radius: 20px; 
                    outline: none; 
                    font-family: inherit; 
                    font-size: 14px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    resize: none; 
                    max-height: 100px; 
                    line-height: 1.5;
                    overflow-y: auto;
                }
                
                .chat-input-area button { 
                    padding: 12px 20px; 
                    margin-right: 10px; 
                    background: #3498db; 
                    color: white; 
                    border: none; 
                    border-radius: 25px; 
                    cursor: pointer; 
                    font-family: inherit; 
                    font-weight: bold;
                    transition: background 0.3s;
                    height: 45px;
                    display: flex;
                    align-items: center;
                }
                .chat-input-area button:hover { background: #2980b9; }
                .chat-input-area button:disabled { background: #ccc; cursor: not-allowed; }

                .typing-indicator { display: flex; gap: 4px; padding: 12px 18px; background: white; border-radius: 15px; border-top-left-radius: 0; width: fit-content; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
                .typing-indicator span { width: 6px; height: 6px; background-color: #999; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; }
                .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
                .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
                @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

                /* ========================================== */
                /* 🖥️ تنظیمات مخصوص دسکتاپ (کامپیوتر) */
                /* ========================================== */
                @media (min-width: 768px) {
                    .chat-container { 
                        max-width: 800px; /* عریض‌تر در کامپیوتر */
                        height: 90dvh;    /* پنجره شناور در وسط صفحه */
                        border-radius: 20px; /* گوشه‌های گرد */
                        box-shadow: 0 10px 30px rgba(0,0,0,0.3); /* سایه زیبا */
                        border: 1px solid rgba(0,0,0,0.1);
                    }
                    
                    .chat-header { 
                        border-top-left-radius: 20px; 
                        border-top-right-radius: 20px; 
                        padding: 15px 20px;
                    }
                    
                    .chat-input-area { 
                        border-bottom-left-radius: 20px; 
                        border-bottom-right-radius: 20px; 
                        padding: 15px 20px;
                        padding-bottom: 15px;
                    }
                    
                    .message-bubble { font-size: 15px; } /* فونت کمی بزرگتر در دسکتاپ */
                }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <div class="chat-header">
                    <div class="header-profile">
                        <div class="avatar ai" style="background: white; color: #2c3e50;">🧠</div>
                        <div class="header-info">
                            <h2>مشاور هوش مصنوعی <span class="online-dot"></span></h2>
                            <p>متخصص روابط و احساسات</p>
                        </div>
                    </div>
                    <button class="new-chat-btn" onclick="startNewChat()" title="چت جدید">🗑️</button>
                </div>
                
                <div class="chat-messages" id="chat-box">
                    <!-- پیام‌ها با جاوااسکریپت لود می‌شوند -->
                </div>
                
                <div class="chat-input-area">
                    <textarea id="msg" placeholder="مشکل یا احساس خود را بنویسید..." rows="1"></textarea>
                    <button id="send-btn" onclick="send()">ارسال</button>
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
                    if (confirm("آیا مطمئن هستید که می‌خواهید تاریخچه این گفتگو را پاک کنید و چت جدیدی شروع کنید؟")) {
                        chatHistory = [];
                        localStorage.removeItem('aiCounselorChat');
                        chatBox.innerHTML = '';
                        appendMessageUI('ai', initialGreeting);
                    }
                }

                msgInput.addEventListener('input', function() {
                    this.style.height = 'auto';
                    this.style.height = (this.scrollHeight) + 'px';
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
                    sendBtn.innerText = '...';
                    
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
                        appendMessageUI('ai', "ارتباط برقرار نشد. اینترنت را چک کن و دوباره تلاش کن.");
                        chatHistory.pop(); 
                    } finally {
                        sendBtn.disabled = false;
                        sendBtn.innerText = 'ارسال';
                    }
                }

                function appendMessageUI(role, text) {
                    if (!text || !text.trim()) return; 

                    const row = document.createElement('div');
                    row.className = `message-row ${role}`;
                    
                    const avatar = document.createElement('div');
                    avatar.className = `avatar ${role}`;
                    avatar.innerText = role === 'user' ? '👤' : '🧠';
                    
                    const content = document.createElement('div');
                    content.className = 'message-content';
                    
                    const name = document.createElement('div');
                    name.className = 'sender-name';
                    name.innerText = role === 'user' ? 'شما' : 'مشاور';
                    
                    const bubble = document.createElement('div');
                    bubble.className = 'message-bubble';
                    bubble.innerText = text;
                    
                    content.appendChild(name);
                    content.appendChild(bubble);
                    
                    if (role === 'user') {
                        row.appendChild(content);
                        row.appendChild(avatar);
                    } else {
                        row.appendChild(avatar);
                        row.appendChild(content);
                    }
                    
                    chatBox.appendChild(row);
                    chatBox.scrollTop = chatBox.scrollHeight; 
                }

                function showTypingIndicator() {
                    const id = 'typing-' + Date.now();
                    const row = document.createElement('div');
                    row.className = 'message-row ai';
                    row.id = id;
                    
                    const avatar = document.createElement('div');
                    avatar.className = 'avatar ai';
                    avatar.innerText = '🧠';
                    
                    const typing = document.createElement('div');
                    typing.className = 'typing-indicator';
                    typing.innerHTML = '<span></span><span></span><span></span>';
                    
                    row.appendChild(avatar);
                    row.appendChild(typing);
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
