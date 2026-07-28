import requests
import json
import sys
import io
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=== TESTING TELEGRAM sendPhoto CAPTION LIMIT TRIMMING ===")

bot_token = Config.TELEGRAM_BOT_TOKEN
admin_chat_id = Config.ADMIN_CHAT_ID

# Sample photo URL
sample_photo = "https://pbs.twimg.com/media/GfXxxxxW0AAxxxx?format=jpg&name=large"

# Long text (over 1024 chars)
long_title = "🚨 <b>BREAKING: DefiLlama V2 Unveils Major RWA & Perps Analytics Protocol</b>"
long_body = "💥 <b>DefiLlama</b> " + ("has released a revolutionary real-time yield and RWA analytics dashboard. " * 20)
long_caption = f"{long_title}\n\n{long_body}"

print(f"Original text length: {len(long_caption)} chars (exceeds Telegram 1024 limit)")

# Trim caption for sendPhoto (max 1000 chars)
trimmed_caption = long_caption[:995] + "..." if len(long_caption) > 1000 else long_caption
print(f"Trimmed caption length for sendPhoto: {len(trimmed_caption)} chars")

url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
payload = {
    "chat_id": admin_chat_id,
    "photo": "https://raw.githubusercontent.com/telegramdesktop/tdesktop/dev/Telegram/Resources/art/bg_initial.jpg",
    "caption": trimmed_caption,
    "parse_mode": "HTML"
}

resp = requests.post(url, json=payload, timeout=10)
print(f"sendPhoto status: {resp.status_code}")
if resp.status_code == 200:
    print("✅ SUCCESS: sendPhoto with trimmed caption delivered photo cleanly!")
else:
    print(f"Error: {resp.text}")
