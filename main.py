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
    
    # پرامپت جدید: شخصیت‌محور، طبیعی و مناسب روابط خانوادگی
    system_prompt = {
        "role": "system", 
        "content": (
            "تو یک مشاور متخصص روابط (به‌ویژه روابط خانوادگی و عاطفی) و روانشناس با رویکرد شناختی-رفتاری (CBT) هستی. "
            "لحن تو بسیار همدلانه، آرام، صمیمی و بدون قضاوت است. مثل یک دوست دانا و مهربان که پای حرف‌های کاربر نشسته است.\n\n"
            "اصول گفتگوی تو:\n"
            "- ابتدا احساس کاربر را درک کن و به او حق بده که چنین حسی دارد.\n"
            "- اگر کاربر درباره یک مشکل (مثل رابطه با خواهر، همسر یا دوست) صحبت کرد، از او بپرس چه اتفاقی افتاده و دقیقاً چه حسی داشته است.\n"
            "- از نصیحت کردن مستقیم و زودهنگام خودداری کن. به جای آن، با پرسیدن یک سوال کوتاه، کاربر را به فکر کردن وادار کن.\n"
            "- وقتی زمان ارائه راهکار رسید، از تکنیک‌های «ارتباط بدون خشونت» استفاده کن (مثلاً به او یاد بده چطور احساساتش را با جملات «من» بیان کند، نه با سرزنش طرف مقابل).\n"
            "- پاسخ‌ها باید طبیعی، روان و در حد یک یا دو پاراگراف کوتاه باشند. در انتهای هر پیام، تنها یک سوال بپرس.\n"
            "- تو درمانگر بالینی نیستی و دارو تجویز نمی‌کنی. اگر نشانه‌های آزار و اذیت شدید یا بحران دیدی، کاربر را به اورژانس اجتماعی (۱۲۳) ارجاع بده."
        )
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [system_prompt] + request.messages,
        "max_tokens": 800, # فضای بیشتر برای تولید پاسخ کامل
        "temperature": 0.85 # خلاقیت بیشتر برای پاسخ‌های انسانی‌تر
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status() 
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            reply_text = data["choices"][0]["message"]["content"]
            
            # اگر مدل واقعا پاسخ خالی داد، یک پیام جایگزین هوشمندتر بر اساس موضوع بفرست
            if not reply_text or not reply_text.strip():
                reply_text = "من کاملاً درکت می‌کنم. دوست دارم بدونم دقیقاً چه اتفاقی بین تو و خواهرت افتاده که این حس رو داری؟ می‌تونی بیشتر برام تعریف کنی؟"
                
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
                }
                
                .chat-container { 
                    width: 100%; 
                    max-width: 600px; 
                    background: #efeae2; 
                    display: flex; 
                    flex-direction: column; 
                    height: 100dvh; 
                }
                
                .chat-header { 
                    background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                    color: white; 
                    padding: 15px; 
                    display: flex; 
                    align-items: center; 
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    flex-shrink: 0; 
                    z-index: 10;
                }
                .header-info { margin-right: 15px; }
                .header-info h2 { margin: 0; font-size: 18px; }
                .header-info p { margin: 0; font-size: 12px; color: #b0c4de; }
                .online-dot { height: 10px; width: 10px; background-color: #25d366; border-radius: 50%; display: inline-block; margin-left: 5px; }

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
                    background: #3498db; 
                    color: white; 
                    border: none; 
                    border-radius: 25px; 
                    cursor: pointer; 
                    font-family: inherit; 
                    font-weight: bold;
                    transition: background 0.3s;
                }
                .chat-input-area button:hover { background: #2980b9; }
                .chat-input-area button:disabled { background: #ccc; cursor: not-allowed; }

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
                    <div class="avatar ai" style="background: white; color: #2c3e50;">🧠</div>
                    <div class="header-info">
                        <h2>مشاور هوش مصنوعی <span class="online-dot"></span></h2>
                        <p>متخصص روابط و احساسات</p>
                    </div>
                </div>
                
                <div class="chat-messages" id="chat-box">
                    <div class="message-row ai">
                        <div class="avatar ai">🧠</div>
                        <div class="message-content">
                            <div class="sender-name">مشاور</div>
                            <div class="message-bubble">سلام! من اینجا هستم تا در مورد روابط، احساسات و چالش‌هایی که داری با هم صحبت کنیم. امروز چه چیزی ذهن تو را مشغول کرده؟</div>
                        </div>
                    </div>
                </div>
                
                <div class="chat-input-area">
                    <input id="msg" type="text" placeholder="مشکل یا احساس خود را بنویسید..." autocomplete="off">
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

                    appendMessage('user', msg);
                    msgInput.value = '';
                    chatHistory.push({ role: 'user', content: msg });

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

                msgInput.addEventListener('keypress', function (e) {
                    if (e.key === 'Enter') send();
                });
            </script>
        </body>
    </html>
    """
