import sys
import io
import json
import requests
from config import Config
from database import Database
from telegram_publisher import TelegramPublisher

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)
db = Database(Config.DATABASE_PATH)

post_id = 37
post = db.get_pending_post(post_id)
print(f"Testing publishing post #{post_id} to channel {Config.TELEGRAM_CHAT_ID}...")
print(f"Title: {post['title']}")
print(f"Text: {post['post_text']}")

# 1. Test direct send to channel
print("\nAttempting send_to_channel...")
res = publisher.send_to_channel(post["title"], post["post_text"], post["has_media"], post["media_urls"])
print(f"send_to_channel result: {res}")

# Let's also check Telegram API response directly
formatted_text = f"{post['title']}\n\n{post['post_text']}"
url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": Config.TELEGRAM_CHAT_ID,
    "text": formatted_text,
    "parse_mode": "HTML",
    "disable_web_page_preview": False
}
r = requests.post(url, json=payload, timeout=10)
print(f"Direct API call to {Config.TELEGRAM_CHAT_ID}: status={r.status_code}, response={r.text}")
