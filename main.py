import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

app = FastAPI()

API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/v1/chat/completions"

# استفاده از مدل پایدار Qwen
MODEL_NAME = "@cf/qwen/qwen3.8-27b"

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
    
    # پرامپت سیستمی ارتقا یافته بر اساس اصول درمان شناختی-رفتاری (CBT)
    system_prompt = {
        "role": "system", 
        "content": (
            "تو یک «همراه هوش مصنوعی» هستی که با اصول درمان شناختی-رفتاری (CBT) آشناست. "
            "هدف تو گوش دادن با حوصله، همدلی و کمک به کاربر برای شناسایی افکار منفی و پیدا کردن راهکارهای عملی است. "
            "تو یک درمانگر رسمی نیستی و حق تشخیص یا تجویز دارو نداری.\n\n"
            "قوانین گفتگو:\n"
            "۱. همیشه ابتدا احساس کاربر را تایید کن (مثلاً: «کاملاً درک می‌کنم که این شرایط چقدر می‌تونه خسته‌کننده باشه»).\n"
            "۲. از دادن نصیحت یا راهکار زودهنگام (مثل تنفس عمیق یا ورزش) در پیام‌های اول خودداری کن. اول باید بفهمی چه چیزی او را آزار می‌دهد.\n"
            "۳. با حوصله و با پرسیدن سوالات ساده (سوالات سقراطی) کمک کن تا افکار منفی‌اش را کشف کند (مثلاً: «وقتی این اتفاق افتاد، چه فکری از ذهنت گذشت؟» یا «چه شواهدی برای درست بودن این فکر داری؟»).\n"
            "۴. پاسخ‌ها باید کوتاه، محاوره‌ای و طبیعی باشند (حداکثر ۳ جمله). هرگز از اصطلاحات پیچیده پزشکی استفاده نکن.\n"
            "۵. در هر پیام فقط یک سوال بپرس.\n"
            "۶. اگر کاربر نشانه‌هایی از بحران شدید یا آسیب به خود نشان داد، با لحنی دلسوزانه او را به اورژانس اجتماعی (۱۲۳) یا صدای مشاور (۱۴۸۰) ارجاع بده."
        )
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [system_prompt] + request.messages,
        "max_tokens": 400,
        "temperature": 0.6  # کمی کاهش دما برای پاسخ‌های متمرکزتر
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status() 
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            reply_text = data["choices"][0]["message"]["content"]
            # جلوگیری از ارسال پیام خالی توسط هوش مصنوعی
            if not reply_text or not reply_text.strip():
                reply_text = "متاسفم، حواسم پرت شد. می‌تونی بیشتر برام بگی چه حسی داری؟"
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
            <title>همراه هوش مصنوعی</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
                
                /* استفاده از dvh برای سازگاری بهتر با مرورگرهای موبایل */
                html, body { height: 100%; margin: 0; padding: 0; overflow: hidden; }
                
                body { 
                    font-family: 'Vazirmatn', Tahoma, sans-serif; 
                    background-color: #e5ddd5; 
                    display: flex; 
                    justify-content: center; 
                }
                
                .chat-container { 
                    width: 100%; 
                    max-width: 600px; 
                    background: #efeae2; 
                    display: flex; 
                    flex-direction: column; 
                    height: 100dvh; /* ارتفاع داینامیک برای موبایل */
                }
                
                /* هدر ثابت در بالای صفحه */
                .chat-header { 
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
                    color: white; 
                    padding: 15px; 
                    display: flex; 
                    align-items: center; 
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    flex-shrink: 0; /* جلوگیری از کوچک شدن هدر */
                    z-index: 10;
                }
                .header-info { margin-right: 15px; }
                .header-info h2 { margin: 0; font-size: 18px; }
                .header-info p { margin: 0; font-size: 12px; color: #b0c4de; }
                .online-dot { height: 10px; width: 10px; background-color: #25d366; border-radius: 50%; display: inline-block; margin-left: 5px; }

                /* ناحیه پیام‌ها با قابلیت اسکرول */
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
                .avatar.ai { background: #ff9800; color: white; margin-right: 10px; }

                .message-content { max-width: 75%; display: flex; flex-direction: column; }
                .message-row.user .message-content { align-items: flex-end; }
                .message-row.ai .message-content { align-items: flex-start; }
                
                .sender-name { font-size: 11px; color: #666; margin-bottom: 3px; margin-right: 5px; margin-left: 5px;}
                
                .message-bubble { 
                    padding: 10px 15px; 
                    border-radius: 15px; 
                    line-height: 1.6; 
                    font-size: 14px; 
                    word-wrap: break-word; 
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                    position: relative;
                }
                .message-row.user .message-bubble { background: #dcf8c6; border-top-right-radius: 0; }
                .message-row.ai .message-bubble { background: white; border-top-left-radius: 0; }

                /* ناحیه ارسال پیام */
                .chat-input-area { 
                    display: flex; 
                    padding: 10px 12px; 
                    padding-bottom: calc(10px + env(safe-area-inset-bottom)); /* رعایت حاشیه پایین گوشی‌های ناچ‌دار */
                    background: #f0f0f0; 
                    border-top: 1px solid #ddd; 
                    flex-shrink: 0;
                }
                .chat-input-area input { 
                    flex: 1; 
                    padding: 12px 15px; 
                    border: none; 
                    border-radius: 25px; 
                    outline: none; 
                    font-family: inherit; 
                    font-size: 14px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                .chat-input-area button { 
                    padding: 0 20px; 
                    margin-right: 10px; 
                    background: #007bff; 
                    color: white; 
                    border: none; 
                    border-radius: 25px; 
                    cursor: pointer; 
                    font-family: inherit; 
                    font-weight: bold;
                    transition: background 0.3s;
                }
                .chat-input-area button:hover { background: #0056b3; }
                .chat-input-area button:disabled { background: #ccc; cursor: not-allowed; }

                /* انیمیشن تایپ */
                .typing-indicator { display: flex; gap: 4px; padding: 12px 18px; background: white; border-radius: 15px; border-top-left-radius: 0; width: fit-content; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
                .typing-indicator span { width: 6px; height: 6px; background-color: #999; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; }
                .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
                .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
                @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <div class="chat-header">
                    <div class="avatar ai" style="background: white; color: #1e3c72;">🤖</div>
                    <div class="header-info">
                        <h2>همراه هوش مصنوعی <span class="online-dot"></span></h2>
                        <p>اینجا هستم تا با هم گفتگو کنیم</p>
                    </div>
                </div>
                
                <div class="chat-messages" id="chat-box">
                    <div class="message-row ai">
                        <div class="avatar ai">🤖</div>
                        <div class="message-content">
                            <div class="sender-name">همراه</div>
                            <div class="message-bubble">سلام! خوشحالم که اینجایی. امروز چه خبر؟ چه چیزی ذهن تو را مشغول کرده؟</div>
                        </div>
                    </div>
                </div>
                
                <div class="chat-input-area">
                    <input id="msg" type="text" placeholder="پیام خود را بنویسید..." autocomplete="off">
                    <button id="send-btn" onclick="send()">ارسال</button>
                </div>
            </div>
            
            <script>
                let chatHistory = []; 
                const chatBox = document.getElementById('chat-box');
                const msgInput = document.getElementById('msg');

                async function send() {
                    const msg = msgInput.value.trim();
                    if (!msg) return;

                    // 1. نمایش پیام کاربر
                    appendMessage('user', msg);
                    msgInput.value = '';
                    chatHistory.push({ role: 'user', content: msg });

                    // 2. نمایش انیمیشن تایپ و قفل کردن دکمه
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

                        // 3. حذف انیمیشن و نمایش پاسخ
                        removeTypingIndicator(typingId);
                        appendMessage('ai', reply);
                        chatHistory.push({ role: 'assistant', content: reply });

                    } catch(e) {
                        removeTypingIndicator(typingId);
                        appendMessage('ai', "ارتباط برقرار نشد. اینترنت را چک کن و دوباره تلاش کن.");
                        chatHistory.pop(); 
                    } finally {
                        sendBtn.disabled = false;
                    }
                }

                function appendMessage(role, text) {
                    if (!text || !text.trim()) return; // اگر متن خالی بود، پیام نمایش داده نشود

                    const row = document.createElement('div');
                    row.className = `message-row ${role}`;
                    
                    const avatar = document.createElement('div');
                    avatar.className = `avatar ${role}`;
                    avatar.innerText = role === 'user' ? '👤' : '🤖';
                    
                    const content = document.createElement('div');
                    content.className = 'message-content';
                    
                    const name = document.createElement('div');
                    name.className = 'sender-name';
                    name.innerText = role === 'user' ? 'شما' : 'همراه';
                    
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
                    avatar.innerText = '🤖';
                    
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

                msgInput.addEventListener('keypress', function (e) {
                    if (e.key === 'Enter') send();
                });
            </script>
        </body>
    </html>
    """
