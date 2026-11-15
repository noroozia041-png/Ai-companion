import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

app = FastAPI()

API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/v1/chat/completions"

# مدل جدید، پایدار و مناسب زبان فارسی
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
    
    system_prompt = {
        "role": "system", 
        "content": "تو یک همراه خودیاری هستی، نه درمانگر. تشخیص نمی‌دهی و دارو تجویز نمی‌کنی. اگر نشانه‌های خطر دیدی، کاربر را به اورژانس روان‌پزشکی ارجاع بده. لحنت همدلانه، محاوره‌ای و کوتاه باشد."
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [system_prompt] + request.messages,
        "max_tokens": 512,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status() 
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            return {"reply": data["choices"][0]["message"]["content"]}
        else:
            return {"reply": f"پاسخ نامشخص از سرور: {data}"}
            
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
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>همراه هوش مصنوعی</title>
            <style>
                body { font-family: Tahoma, sans-serif; background-color: #f0f2f5; margin: 0; padding: 15px; display: flex; justify-content: center; }
                .chat-container { width: 100%; max-width: 500px; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); display: flex; flex-direction: column; height: 85vh; overflow: hidden; }
                .chat-header { background: #007bff; color: white; padding: 15px; text-align: center; font-weight: bold; font-size: 18px; }
                .chat-messages { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; background: #e5ddd5; }
                .message { max-width: 80%; padding: 10px 14px; border-radius: 15px; line-height: 1.5; font-size: 15px; word-wrap: break-word; }
                .message.user { background: #dcf8c6; align-self: flex-end; border-bottom-right-radius: 2px; }
                .message.ai { background: white; align-self: flex-start; border-bottom-left-radius: 2px; }
                .chat-input-area { display: flex; padding: 10px; background: white; border-top: 1px solid #ddd; }
                .chat-input-area input { flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 20px; outline: none; font-family: inherit; }
                .chat-input-area button { padding: 10px 20px; margin-right: 8px; background: #007bff; color: white; border: none; border-radius: 20px; cursor: pointer; font-family: inherit; font-size: 15px; }
                .chat-input-area button:hover { background: #0056b3; }
                .chat-input-area button:disabled { background: #ccc; cursor: not-allowed; }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <div class="chat-header">همراه هوش مصنوعی</div>
                <div class="chat-messages" id="chat-box">
                    <div class="message ai">سلام! من اینجا هستم تا در کنارت باشم. امروز حالت چطوره؟</div>
                </div>
                <div class="chat-input-area">
                    <input id="msg" type="text" placeholder="پیام خود را بنویسید..." autocomplete="off">
                    <button id="send-btn" onclick="send()">ارسال</button>
                </div>
            </div>
            <script>
                let chatHistory = []; 

                async function send() {
                    const input = document.getElementById('msg');
                    const msg = input.value.trim();
                    if (!msg) return;

                    appendMessage('user', msg);
                    input.value = '';
                    
                    chatHistory.push({ role: 'user', content: msg });

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

                        appendMessage('ai', reply);
                        chatHistory.push({ role: 'assistant', content: reply });

                    } catch(e) {
                        appendMessage('ai', "خطا در ارتباط با سرور. دوباره تلاش کنید.");
                        chatHistory.pop(); 
                    } finally {
                        sendBtn.disabled = false;
                        sendBtn.innerText = 'ارسال';
                    }
                }

                function appendMessage(role, text) {
                    const chatBox = document.getElementById('chat-box');
                    const msgDiv = document.createElement('div');
                    msgDiv.className = `message ${role}`;
                    msgDiv.innerText = text;
                    chatBox.appendChild(msgDiv);
                    chatBox.scrollTop = chatBox.scrollHeight; 
                }

                document.getElementById('msg').addEventListener('keypress', function (e) {
                    if (e.key === 'Enter') send();
                });
            </script>
        </body>
    </html>
    """
