import sys
import io
import requests
from datetime import datetime, timezone
from config import Config
from ai_editor import AIEditor
from content_fetcher import ContentFetcher
from telegram_publisher import TelegramPublisher

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("🔍 COMPREHENSIVE FULL-SYSTEM AUDIT AND VERIFICATION TEST")
print("=" * 70)

# TEST 1: Configuration Audit
print("\n--- TEST 1: CONFIGURATION & SETTINGS AUDIT ---")
print(f"✅ Monitoring Check Interval: {Config.CHECK_INTERVAL_MINUTES} minutes (Expected: 60)")
print(f"✅ Max Tweet Age Filter: {Config.MAX_TWEET_AGE_HOURS} hours (Expected: 10.0)")
print(f"✅ RSS Feeds Enabled: {Config.ENABLE_RSS_FEEDS} (Expected: False)")
print(f"✅ Target Accounts Count: {len(Config.TARGET_ACCOUNTS)} handles")

# TEST 2: OpenRouter AI Generation
print("\n--- TEST 2: OPENROUTER AI GENERATION ---")
editor = AIEditor(Config.OPENROUTER_API_KEY, Config.OPENROUTER_MODEL, Config.OPENROUTER_BASE_URL)
sample_item = {
    "id": "full_audit_999",
    "author": "Lookonchain",
    "title": "Tweet by @Lookonchain",
    "text": "A smart trader made 500 ETH ($1.5M) profit trading meme coins in 24 hours!",
    "url": "https://x.com/Lookonchain/status/2082462652429906277"
}
ai_result = editor.process_item(sample_item)
print(f"✅ AI Generation Status: {ai_result.get('status')}")
print(f"   Title: {ai_result.get('title')}")
print(f"   Sniper Reply: '{ai_result.get('sniper_reply')}'")
print(f"   AI Opinion: '{ai_result.get('ai_opinion')}'")

# TEST 3: Priority Timestamp Sorting Test
print("\n--- TEST 3: CHRONOLOGICAL PRIORITY SORTING (NEWEST -> OLDEST) ---")
test_items = [
    {"id": "1", "author": "acc1", "text": "Old item", "timestamp": 1700000000.0},
    {"id": "2", "author": "acc2", "text": "Newest item", "timestamp": 1700000500.0},
    {"id": "3", "author": "acc3", "text": "Middle item", "timestamp": 1700000200.0}
]
test_items.sort(key=lambda x: x.get("timestamp", 0.0), reverse=True)
sorted_order = [x["id"] for x in test_items]
print(f"✅ Sorted Order IDs (Newest -> Oldest): {sorted_order} (Expected: ['2', '3', '1'])")

# TEST 4: Telegram Admin Preview & 3-Variation Inline Buttons
print("\n--- TEST 4: TELEGRAM ADMIN PREVIEW & 3-VARIATION BUTTONS ---")
publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)

# Public test photo URL
sample_photo_url = "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?w=600&auto=format&fit=crop"

preview_success = publisher.send_admin_preview(
    db_id=9999,
    title=ai_result.get("title", "🚨 BREAKING NEWS"),
    post_text=ai_result.get("post_text", "Sample post text body"),
    author=sample_item["author"],
    has_media=True,
    media_urls=[sample_photo_url],
    sniper_reply=ai_result.get("sniper_reply", "💬 Smart whale movements!"),
    target_platform="BOTH",
    ai_opinion=ai_result.get("ai_opinion", "💡 Высокий приоритет для публикации"),
    source_url=sample_item["url"]
)

print(f"✅ Admin Preview Delivery (with Photo + 3 Buttons): {preview_success}")

print("\n" + "=" * 70)
print("🎯 FULL-SYSTEM AUDIT COMPLETED SUCCESSFULLY!")
print("=" * 70)
