import requests
import json
import sys
import io
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("1. Testing Telegram Bot Token...")
try:
    r = requests.get(f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/getMe", timeout=5)
    print(f"   Telegram Status: {r.status_code}, Response: {r.json()}")
except Exception as e:
    print(f"   Telegram Error: {e}")

print("2. Testing OpenRouter API...")
try:
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {Config.OPENROUTER_API_KEY}"},
        json={"model": Config.OPENROUTER_MODEL, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 10},
        timeout=10
    )
    print(f"   OpenRouter Status: {r.status_code}")
    if r.status_code != 200:
        print(f"   OpenRouter Response: {r.text}")
    else:
        print(f"   OpenRouter Output: {r.json()['choices'][0]['message']['content']}")
except Exception as e:
    print(f"   OpenRouter Error: {e}")
