import requests
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

bot_token = "8861390593:AAF2vk67cWiY354F84siLV6UzyxcyuKuXHQ"
numeric_chat_id = "-1004301846312"

print(f"Testing sendMessage to numeric chat ID: {numeric_chat_id}")
r = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
    "chat_id": numeric_chat_id,
    "text": "🧪 Test message from bot daemon"
})
print(f"Response: status={r.status_code}, body={r.json()}")
