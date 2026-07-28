import requests
import sys
import io
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

bot_token = Config.TELEGRAM_BOT_TOKEN

print(f"Bot Token: {bot_token}")

# 1. getMe
me = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe").json()
print("getMe:", me)

# 2. getChat for @influencer_logic
chat_handle = requests.get(f"https://api.telegram.org/bot{bot_token}/getChat", params={"chat_id": "@influencer_logic"}).json()
print("getChat (@influencer_logic):", chat_handle)

# 3. getChatMember for bot in @influencer_logic
bot_id = me.get("result", {}).get("id")
member = requests.get(f"https://api.telegram.org/bot{bot_token}/getChatMember", params={"chat_id": "@influencer_logic", "user_id": bot_id}).json()
print("getChatMember in @influencer_logic:", member)

# 4. Try sending to @influencer_logic
send_handle = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={"chat_id": "@influencer_logic", "text": "Test"}).json()
print("sendMessage (@influencer_logic):", send_handle)

# 5. Try sending to -1004301846312
send_num = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={"chat_id": "-1004301846312", "text": "Test"}).json()
print("sendMessage (-1004301846312):", send_num)
