import requests
import sys
import io
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

bot_token = Config.TELEGRAM_BOT_TOKEN
chat_id = Config.TELEGRAM_CHAT_ID

print(f"Bot Token: {bot_token[:10]}...")
print(f"Target Chat ID: {chat_id}")

# 1. Test getMe to confirm Bot Username
r = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe")
print(f"getMe response: {r.json()}")

# 2. Test getChat for TELEGRAM_CHAT_ID
r2 = requests.get(f"https://api.telegram.org/bot{bot_token}/getChat", params={"chat_id": chat_id})
print(f"getChat response for {chat_id}: {r2.json()}")

# 3. Test sendMessage to TELEGRAM_CHAT_ID
r3 = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={"chat_id": chat_id, "text": "Test message from CryptoBot"})
print(f"sendMessage response to {chat_id}: {r3.json()}")

# 4. Check getUpdates to see if channel posts or member updates exist
r4 = requests.get(f"https://api.telegram.org/bot{bot_token}/getUpdates")
print(f"getUpdates response: {r4.json()}")
