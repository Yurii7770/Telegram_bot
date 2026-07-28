import requests
import time
import sys
import io
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

bot_token = Config.TELEGRAM_BOT_TOKEN
channel_id = Config.TELEGRAM_CHAT_ID

print("=== Checking Telegram Bot Membership Status ===")
print(f"Bot Username: @Cryptocurrencyworkingbot (ID: 8861390593)")
print(f"Target Channel: {channel_id} (@influencer_logic)")

r = requests.get(f"https://api.telegram.org/bot{bot_token}/getChatMember", params={
    "chat_id": channel_id,
    "user_id": 8861390593
})

print(f"getChatMember Result: {r.json()}")
