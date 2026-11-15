import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

app = FastAPI()

API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/v1/chat/completions"

# مدل جدید و معتبر در کلادفلر
MODEL_NAME = "@cf/qwen/qwen1.5-7b-chat-awq"

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
            {
                "role": "system", 
                "content": "تو یک همراه خودیاری هستی، نه درمانگر. تشخیص نمی‌دهی و دارو تجویز نمی‌کنی. اگر نشانه‌های خطر دیدی، کاربر را به اورژانس روان‌پزشکی ارجاع بده. لحنت همدلانه، محاوره‌ای و کوتاه باشد."
            },
            {"role": "user", "content": request.message}
        ],
        "max_tokens": 512,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        # این خط بررسی می‌کند که آیا کلادفلر خطا داده است یا خیر
        response.raise_for_status() 
        
        data = response.json()
        
        # بررسی اینکه آیا پاسخ ساختار درستی دارد
        if "choices" in data and len(data["choices"]) > 0:
            return {"reply": data["choices"][0]["message"]["content"]}
        else:
            return {"reply": f"پاسخ نامشخص از سرور: {data}"}
            
    except Exception as e:
        # در صورت بروز خطا، متن دقیق خطا را برمی‌گرداند تا بتوانیم عیب‌یابی کنیم
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
                body { font-family: Tahoma, sans-serif; padding: 20px; text-align: center; background-color: #f9f9f9; }
                .container { max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                input { width: 90%; padding: 12px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 5px; font-family: inherit; }
                button { padding: 12px 25px; background: #007bff; color: white; border: none; border-radius: 5px; font-family: inherit; cursor: pointer; font-size: 16px; width: 100%; }
                button:hover { background: #0056b3; }
                #res { margin-top: 20px; background: #f1f1f1; padding: 15px; border-radius: 5px; min-height: 60px; text-align: right; line-height: 1.6; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>همراه هوش مصنوعی</h2>
                <input id="msg" type="text" placeholder="امروز چطور هستی؟..." autocomplete="off">
                <button onclick="send()">ارسال پیام</button>
                <div id="res">پاسخ در اینجا نمایش داده می‌شود...</div>
            </div>
            <script>
                async function send() {
                    const msg = document.getElementById('msg').value;
                    const resElement = document.getElementById('res');
                    
                    if (!msg.trim()) {
                        resElement.innerText = "لطفاً یک پیام بنویسید.";
                        return;
                    }
                    
                    resElement.innerText = "در حال فکر کردن...";
                    document.getElementById('msg').value = ''; // پاک کردن کادر متن
                    
                    try {
                        const res = await fetch('/chat', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({message: msg})
                        });
                        const data = await res.json();
                        resElement.innerText = data.reply || data.detail || "خطای نامشخص";
                    } catch(e) {
                        resElement.innerText = "خطا در ارتباط با سرور. دوباره تلاش کنید.";
                    }
                }
                
                // ارسال با زدن دکمه Enter
                document.getElementById('msg').addEventListener('keypress', function (e) {
                    if (e.key === 'Enter') send();
                });
            </script>
        </body>
    </html>
    """
