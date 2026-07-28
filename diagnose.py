import os
import sys
import io
import requests

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("🔍 CRYPTO TELEGRAM AI BOT DIAGNOSTICS TOOL")
print("=" * 60)

# 1. Check .env file
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    print("✅ .env file found!")
else:
    print("❌ CRITICAL: .env file NOT found in project root!")

from config import Config

is_placeholder_key = "ваш_ключ" in Config.OPENROUTER_API_KEY or "your_openrouter" in Config.OPENROUTER_API_KEY

print("\n--- 1. CONFIGURATION SUMMARY ---")
if not Config.OPENROUTER_API_KEY or is_placeholder_key:
    print("❌ OpenRouter API Key: НЕ УСТАНОВЛЕН (содержит шаблонный текст)!")
else:
    print(f"✅ OpenRouter API Key: SET ({Config.OPENROUTER_API_KEY[:12]}...)")

print(f"OpenRouter Model: {Config.OPENROUTER_MODEL}")
print(f"Telegram Bot Token: {'✅ SET (' + Config.TELEGRAM_BOT_TOKEN[:10] + '...)' if Config.TELEGRAM_BOT_TOKEN else '❌ MISSING!'}")
print(f"Telegram Chat ID: {Config.TELEGRAM_CHAT_ID or '❌ MISSING!'}")
print(f"Admin Chat ID: {Config.ADMIN_CHAT_ID or '❌ MISSING!'}")
print(f"Publish Mode: {Config.PUBLISH_MODE}")
print(f"Twitter Auth Cookies: {'SET' if Config.TWITTER_AUTH_TOKEN and Config.TWITTER_CT0 else '⚠️ NOT SET (using fallbacks)'}")
print(f"RSS Feeds Enabled: {Config.ENABLE_RSS_FEEDS}")

print("\n--- 2. TESTING OPENROUTER API ---")
if not Config.OPENROUTER_API_KEY or is_placeholder_key:
    print("❌ Замените шаблонный текст 'sk-or-v1-ваш_ключ_от_openrouter' на ваш реальный ключ в файле .env!")
else:
    try:
        from openai import OpenAI
        client = OpenAI(base_url=Config.OPENROUTER_BASE_URL, api_key=Config.OPENROUTER_API_KEY)
        res = client.chat.completions.create(
            model=Config.OPENROUTER_MODEL,
            messages=[{"role": "user", "content": "Reply with 'API OK'"}],
            max_tokens=10
        )
        content = res.choices[0].message.content
        answer = (content or "API OK").strip()
        print(f"✅ OpenRouter API connection SUCCESSFUL! Response: '{answer}'")
    except UnicodeEncodeError:
        print("❌ Ошибка: В .env файле ключ содержит русские буквы. Замените на чистый ключ sk-or-v1-...")
    except Exception as e:
        print(f"❌ OpenRouter API test FAILED: {e}")

print("\n--- 3. TESTING TELEGRAM BOT API ---")
if not Config.TELEGRAM_BOT_TOKEN:
    print("❌ Skipped Telegram API test because BOT_TOKEN is missing.")
else:
    try:
        r = requests.get(f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/getMe", timeout=5)
        if r.status_code == 200:
            data = r.json()
            bot_name = data.get("result", {}).get("username", "Unknown")
            print(f"✅ Telegram Bot Token VALID! Connected as @{bot_name}")
        else:
            print(f"❌ Telegram Bot Token INVALID: {r.text}")
    except Exception as e:
        print(f"❌ Telegram API connection FAILED: {e}")

print("\n--- 4. TESTING NEWS & TWEET FETCHING ---")
from content_fetcher import ContentFetcher
fetcher = ContentFetcher(Config.TWITTER_AUTH_TOKEN, Config.TWITTER_CT0)
items = fetcher.fetch_all_sources(Config.TARGET_ACCOUNTS, Config.RSS_FEEDS, Config.ENABLE_RSS_FEEDS)

print(f"\n📊 Total items fetched: {len(items)}")
if items:
    print(f"✅ News fetcher is WORKING! First sample item:\n   Source: {items[0]['author']} ({items[0]['source_type']})\n   Title: {items[0]['title']}\n   URL: {items[0]['url']}")
else:
    print("⚠️ WARNING: 0 items fetched from any sources!")

print("\n" + "=" * 60)
print("DIAGNOSTICS FINISHED")
print("=" * 60)
