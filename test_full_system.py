import requests
import sys
import io
from config import Config
from ai_editor import AIEditor
from telegram_publisher import TelegramPublisher

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("🔍 FULL SYSTEM INTEGRATION TEST")
print("=" * 60)

# 1. Test OpenRouter DeepSeek V3
print(f"1. OpenRouter Model: {Config.OPENROUTER_MODEL}")
editor = AIEditor(Config.OPENROUTER_API_KEY, Config.OPENROUTER_MODEL, Config.OPENROUTER_BASE_URL)

sample_item = {
    "id": "full_test_101",
    "author": "DefiLlama",
    "title": "DefiLlama Tracks $100 Billion TVL Across Multi-Chain DeFi",
    "text": "DefiLlama's total value locked (TVL) metrics surpassed $100 billion across 100+ layer-1 and layer-2 blockchains.",
    "url": "https://x.com/DefiLlama/status/1890000000000000000"
}

ai_res = editor.process_item(sample_item)
print(f"AI Generation Status: {ai_res.get('status')}")
if ai_res.get("status") == "POST":
    print(f"Title: {ai_res['title']}")
    print(f"Text snippet: {ai_res['post_text'][:100]}...\n")
else:
    print(f"AI Error/Reason: {ai_res.get('reason')}\n")

# 2. Test Telegram Bot API
publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)

print(f"2. Testing Admin Preview Send to ADMIN_CHAT_ID ({Config.ADMIN_CHAT_ID})...")
sent_admin = publisher.send_admin_preview(
    db_id=888,
    title=ai_res.get("title", "Test Title"),
    post_text=ai_res.get("post_text", "Test Body"),
    author=sample_item["author"]
)
print(f"Admin Preview Result: {sent_admin}")

print(f"\n3. Testing Direct Channel Send to TELEGRAM_CHAT_ID ({Config.TELEGRAM_CHAT_ID})...")
sent_channel, err_msg = publisher.send_to_channel(
    title=ai_res.get("title", "Test Title"),
    post_text=ai_res.get("post_text", "Test Body")
)
print(f"Channel Publish Result: {sent_channel} (Error: {err_msg})")

print("=" * 60)
