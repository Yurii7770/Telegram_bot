import sys
import io
import json
from config import Config
from ai_editor import AIEditor
from telegram_publisher import TelegramPublisher

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=== TESTING SNIPER REPLY GENERATION FOR TWITTER STRATEGY ===")
editor = AIEditor(Config.OPENROUTER_API_KEY, Config.OPENROUTER_MODEL, Config.OPENROUTER_BASE_URL)
publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)

sample_item = {
    "id": "sniper_test_201",
    "author": "vitalikbuterin",
    "title": "Vitalik Buterin Outlines Future Scale Roadmap for L2 Protocols",
    "text": "Vitalik Buterin has released a new blog post detailing the roadmap for L2 gas reduction, rollups interop, and state expiry.",
    "url": "https://x.com/vitalikbuterin/status/1899999999999999999"
}

res = editor.process_item(sample_item)
print("AI Result:")
print(json.dumps(res, indent=2, ensure_ascii=False))

if res.get("status") == "POST":
    print("\nSending Admin Preview with Sniper Reply to Telegram...")
    sent = publisher.send_admin_preview(
        db_id=777,
        title=res["title"],
        post_text=res["post_text"],
        author=sample_item["author"],
        sniper_reply=res.get("sniper_reply", "")
    )
    print(f"Admin preview sent: {sent}")
