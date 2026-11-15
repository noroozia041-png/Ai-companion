import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

app = FastAPI()

API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/v1/chat/completions"
MODEL_NAME = "@cf/qwen/qwen2.5-7b-instruct"

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    if not API_TOKEN or not ACCOUNT_ID:
        raise HTTPException(status_code=500, detail="کلیدهای API در ورسل تنظیم نشده‌اند.")
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "تو یک همراه خودیاری هستی، نه درمانگر. تشخیص نمی‌دهی و دارو تجویز نمی‌کنی. اگر نشانه‌های خطر دیدی، کاربر را به اورژانس روان‌پزشکی ارجاع بده. لحنت همدلانه و کوتاه باشد."},
            {"role": "user", "content": request.message}
        ],
        "max_tokens": 512,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return {"reply": data["choices"][0]["message"]["content"]}
    except Exception as e:
        error_detail = response.text if 'response' in locals() else str(e)
        raise HTTPException(status_code=500, detail=f"خطا: {error_detail}")

# این بخش یک صفحه ساده می‌سازد تا بتوانید با گوشی تست کنید
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head><meta charset="utf-8"><title>تست هوش مصنوعی</title></head>
        <body style="font-family: sans-serif; padding: 20px; text-align: center;">
            <h2>همراه هوش مصنوعی</h2>
            <input id="msg" type="text" placeholder="پیام خود را بنویسید..." style="width: 80%; padding: 10px; margin-bottom: 10px;">
            <br>
            <button onclick="send()" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px;">ارسال</button>
            <p id="res" style="margin-top: 20px; background: #f0f0f0; padding: 15px; border-radius: 5px; min-height: 50px;">پاسخ در اینجا نمایش داده می‌شود...</p>
            <script>
                async function send() {
                    const msg = document.getElementById('msg').value;
                    const resElement = document.getElementById('res');
                    resElement.innerText = "در حال فکر کردن...";
                    try {
                        const res = await fetch('/chat', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({message: msg})
                        });
                        const data = await res.json();
                        resElement.innerText = data.reply || data.detail;
                    } catch(e) {
                        resElement.innerText = "خطا در ارتباط با سرور";
                    }
                }
            </script>
        </body>
    </html>
    """
