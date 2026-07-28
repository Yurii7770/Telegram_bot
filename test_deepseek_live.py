import sys
import io
import json
from config import Config
from ai_editor import AIEditor
from telegram_publisher import TelegramPublisher

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print(f"Testing Model: {Config.OPENROUTER_MODEL}")
print(f"API Key Present: {'Yes' if Config.OPENROUTER_API_KEY else 'No'}")

editor = AIEditor(Config.OPENROUTER_API_KEY, Config.OPENROUTER_MODEL, Config.OPENROUTER_BASE_URL)
publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)

sample_item = {
    "id": "deepseek_live_001",
    "author": "DefiLlama",
    "title": "DefiLlama Launches Cross-Chain Yield Analytics Engine",
    "text": "DefiLlama has launched its next-gen cross-chain yield analytics engine tracking 6,000+ liquidity pools.",
    "url": "https://x.com/DefiLlama/status/1890000000000000000"
}

print("=== Sending request to DeepSeek V3 via OpenRouter ===")
res = editor.process_item(sample_item)
print(json.dumps(res, indent=2, ensure_ascii=False))

if res.get("status") == "POST":
    print("\n=== Sending preview to Telegram ===")
    sent = publisher.send_admin_preview(
        db_id=100,
        title=res["title"],
        post_text=res["post_text"],
        author=sample_item["author"]
    )
    print(f"Preview sent successfully: {sent}")
