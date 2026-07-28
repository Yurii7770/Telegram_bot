import sys
import io
import json
from config import Config
from ai_editor import AIEditor
from telegram_publisher import TelegramPublisher

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=== TESTING EDITORIAL SEPARATION & AI OPINION GENERATION ===")
editor = AIEditor(Config.OPENROUTER_API_KEY, Config.OPENROUTER_MODEL, Config.OPENROUTER_BASE_URL)
publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)

sample_item = {
    "id": "editorial_test_301",
    "author": "DefiLlama",
    "title": "DefiLlama Integration With Hyperliquid Exceeds $2 Billion Volume",
    "text": "DefiLlama metrics confirm Hyperliquid DEX volume crossed $2B, setting new L2 derivatives record.",
    "url": "https://x.com/DefiLlama/status/1899999999999888888"
}

res = editor.process_item(sample_item)
print("AI Result:")
print(json.dumps(res, indent=2, ensure_ascii=False))

if res.get("status") == "POST":
    print("\nSending Admin Preview with Platform Separation & Russian AI Opinion to Telegram...")
    sent = publisher.send_admin_preview(
        db_id=999,
        title=res["title"],
        post_text=res["post_text"],
        author=sample_item["author"],
        sniper_reply=res.get("sniper_reply", ""),
        target_platform=res.get("target_platform", "BOTH"),
        ai_opinion=res.get("ai_opinion", "")
    )
    print(f"Admin preview sent: {sent}")
