import requests
import io
import sys
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

bot_token = Config.TELEGRAM_BOT_TOKEN
admin_chat = Config.ADMIN_CHAT_ID

sample_photo_url = "https://pbs.twimg.com/media/Gcj5_GKWcAEz6uL?format=jpg&name=large"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

print("Downloading photo from Twitter CDN via local requests session...")
img_resp = requests.get(sample_photo_url, headers=headers, timeout=10)
print(f"Download status: {img_resp.status_code}, Bytes length: {len(img_resp.content)}")

if img_resp.status_code == 200:
    print("Uploading downloaded image bytes to Telegram via Multipart/form-data...")
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    caption = "📸 <b>TEST MULTIPART PHOTO UPLOAD</b>\n\nDirectly uploaded Twitter photo bytes!"
    
    files = {
        "photo": ("image.jpg", img_resp.content, "image/jpeg")
    }
    data = {
        "chat_id": admin_chat,
        "caption": caption,
        "parse_mode": "HTML"
    }
    
    r = requests.post(url, data=data, files=files, timeout=15)
    print(f"Multipart sendPhoto Status: {r.status_code}")
    print(f"Multipart sendPhoto Response: {r.text}")
