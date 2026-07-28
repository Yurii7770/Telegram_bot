import sys
import io
import json
from config import Config
from ai_editor import AIEditor
from telegram_publisher import TelegramPublisher

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

editor = AIEditor(Config.OPENROUTER_API_KEY, Config.OPENROUTER_MODEL, Config.OPENROUTER_BASE_URL)
publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)

sample_item = {
    "id": "test_item_999",
    "author": "DefiLlama",
    "title": "DefiLlama Launches Cross-Chain Yield Aggregator API",
    "text": "DefiLlama has officially released its real-time cross-chain yield aggregator API tracking over 5,000 pools across 80 blockchains.",
    "url": "https://x.com/DefiLlama/status/1890000000000000000"
}

print("=== Generating Post via AI Editor ===")
res = editor.process_item(sample_item)
print(json.dumps(res, indent=2, ensure_ascii=False))

if res.get("status") == "POST":
    print("\n=== Sending Preview to Admin Telegram ===")
    sent = publisher.send_admin_preview(
        db_id=999,
        title=res["title"],
        post_text=res["post_text"],
        author=sample_item["author"]
    )
    print(f"Admin preview sent: {sent}")
