import requests
import sys
import io
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

bot_token = Config.TELEGRAM_BOT_TOKEN
admin_chat = Config.ADMIN_CHAT_ID

print(f"Testing Telegram sendPhoto to Admin Chat ID: {admin_chat}...")

# Test photo URL from Twitter CDN (Lookonchain or DefiLlama media)
sample_photo_url = "https://pbs.twimg.com/media/Gcj5_GKWcAEz6uL?format=jpg&name=large"

url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
caption = "📸 <b>TEST PHOTO PUBLISHING</b>\n\nThis is a test photo from Twitter CDN."

payload = {
    "chat_id": admin_chat,
    "photo": sample_photo_url,
    "caption": caption,
    "parse_mode": "HTML"
}

try:
    r = requests.post(url, json=payload, timeout=10)
    print(f"sendPhoto Status: {r.status_code}")
    print(f"sendPhoto Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")
