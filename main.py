import os
import requests
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

# ==========================================
# 🔑 کلیدهای محیطی (در Vercel تنظیم می‌شوند)
# ==========================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CF_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
CF_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")

# Upstash Redis برای ذخیره تاریخچه چت
UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

CF_URL = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/v1/chat/completions"
MODEL_NAME = "@cf/qwen/qwen3.8-27b"

# ==========================================
# 🎯 پرامپت فوق‌تخصصی (همان پرامپت مرهم)
# ==========================================
SYSTEM_PROMPT = """
[هویت و نقش]
تو «مرهم» هستی؛ یک مشاور روانشناس و متخصص ارشد سلامت روان با ۲۰ سال تجربه بالینی. 
حوزه‌های تخصص تو شامل: روابط (خانوادگی، عاطفی، بین‌فردی)، مدیریت اضطراب و استرس، افسردگی خفیف، تقویت اعتماد به نفس و رشد فردی است.
تو تسلط کامل بر رویکرد «شناختی-رفتاری (CBT)»، «ارتباط بدون خشونت (NVC)» و «نظریه دلبستگی» داری.
تو یک درمانگر بالینی نیستی و حق تشخیص بیماری یا تجویز دارو نداری.

[لحن و شخصیت]
- لحن تو باید بسیار آرام، گرم، همدلانه، بدون قضاوت و سرشار از اطمینان‌بخشی باشد.
- هرگز طرف کسی را نگیر و از کلمات کلیشه‌ای استفاده نکن. مثل یک انسان دانا صحبت کن.

[اصول درمانی]
۱. اعتباربخشی: ابتدا احساس کاربر را تایید کن.
۲. کشف ریشه: نیاز پنهان کاربر را کشف کن.
۳. ابزار عملی: از تکنیک‌های CBT و NVC استفاده کن.
۴. سوالات سقراطی: با سوالات عمیق کاربر را به خودآگاهی برسان.

[ساختار پاسخ‌دهی]
1. آینه‌سازی و همدلی.
2. بازتعریف یا ارائه ابزار (مثال‌ها حتماً با گیومه بسته شوند).
3. سوال پایانی کوتاه.

[خط قرمزها]
- پاسخ‌ها در حد ۲ تا ۳ پاراگراف کوتاه باشند.
- هرگز جمله یا نقل‌قولی را نیمه‌کاره رها نکن.
- اگر نشانه‌های بحران حاد دیدی، کاربر را به اورژانس اجتماعی (۱۲۳) یا صدای مشاور (۱۴۸۰) ارجاع بده.
"""

# ==========================================
# 🗄️ توابع دیتابیس (Upstash Redis)
# ==========================================
def get_chat_history(user_id):
    """دریافت تاریخچه چت کاربر از دیتابیس"""
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        return []
    try:
        res = requests.get(f"{UPSTASH_URL}/get/chat_{user_id}", headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"})
        data = res.json()
        if data.get("result"):
            return json.loads(data["result"])
    except Exception as e:
        print(f"Redis Get Error: {e}")
    return []

def save_chat_history(user_id, history):
    """ذخیره تاریخچه چت (فقط ۱۲ پیام آخر برای صرفه‌جویی در توکن)"""
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        return
    try:
        # محدود کردن به ۱۲ پیام آخر
        history = history[-12:]
        requests.post(
            f"{UPSTASH_URL}/set/chat_{user_id}",
            headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"},
            json=history
        )
    except Exception as e:
        print(f"Redis Set Error: {e}")

# ==========================================
# 🤖 توابع ارتباط با تلگرام
# ==========================================
def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown" # برای بولد شدن و لیست‌ها
    }
    requests.post(url, json=payload)

def send_typing_action(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
    requests.post(url, json={"chat_id": chat_id, "action": "typing"})

# ==========================================
# 🚦 Webhook Endpoint (گوش دادن به تلگرام)
# ==========================================
@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        update = await request.json()
        
        # بررسی اینکه پیام متنی است یا نه
        if "message" not in update or "text" not in update["message"]:
            return JSONResponse(content={"status": "ok"})

        chat_id = update["message"]["chat"]["id"]
        user_id = update["message"]["from"]["id"]
        user_text = update["message"]["text"]

        # دستور /start
        if user_text == "/start":
            welcome_msg = (
                f"سلام {update['message']['from'].get('first_name', 'دوست من')} عزیز! 🍃\n\n"
                "من **مرهم** هستم، همراه و مشاور شما. اینجا هستم تا در مورد روابط، احساسات، "
                "استرس‌ها و چالش‌های زندگی با هم صحبت کنیم.\n\n"
                "همین حالا می‌تونی هر چیزی که ذهنت رو مشغول کرده برام بنویسی..."
            )
            send_telegram_message(chat_id, welcome_msg)
            return JSONResponse(content={"status": "ok"})

        # نمایش وضعیت "در حال تایپ..."
        send_typing_action(chat_id)

        # دریافت تاریخچه
        history = get_chat_history(user_id)
        history.append({"role": "user", "content": user_text})

        # آماده‌سازی درخواست برای کلادفلر
        headers = {
            "Authorization": f"Bearer {CF_API_TOKEN}",
            "Content-Type": "application/json",
            "x-session-affinity": str(user_id) # کشینگ بر اساس آیدی کاربر
        }
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
        
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "max_tokens": 2048,
            "temperature": 0.75 
        }

        # ارسال به کلادفلر
        response = requests.post(CF_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            reply_text = data["choices"][0]["message"]["content"]
            
            # ارسال پاسخ به تلگرام
            send_telegram_message(chat_id, reply_text)

            # ذخیره تاریخچه جدید
            history.append({"role": "assistant", "content": reply_text})
            save_chat_history(user_id, history)
        else:
            send_telegram_message(chat_id, "متاسفانه الان نمی‌تونم پاسخ بدم. دوباره تلاش کن.")

    except Exception as e:
        print(f"Webhook Error: {e}")
    
    return JSONResponse(content={"status": "ok"})

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Marham Telegram Bot is running!"}
