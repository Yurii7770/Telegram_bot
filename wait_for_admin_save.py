import requests
import time
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

bot_token = "8861390593:AAF2vk67cWiY354F84siLV6UzyxcyuKuXHQ"
chat_id = "-1004301846312"

print("Waiting for admin permissions to be saved in Telegram...")
for i in range(15):
    r = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
        "chat_id": chat_id,
        "text": "✅ Тестовая проверка прав бота! Права успешно сохранены!"
    })
    data = r.json()
    if data.get("ok"):
        print("🎉 SUCCESS! Bot is now recognized as admin and message published!")
        break
    else:
        print(f"[{i+1}/15] Still waiting: {data.get('description')}")
    time.sleep(2)
