import sys
import io
import requests
from config import Config
from content_fetcher import ContentFetcher
from telegram_publisher import TelegramPublisher

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=== 1. TESTING IMAGE FETCHING & TELEGRAM PHOTO POSTING ===")
fetcher = ContentFetcher(Config.TWITTER_AUTH_TOKEN, Config.TWITTER_CT0)

# Check target handles for items
items = fetcher.fetch_all_sources(["DefiLlama", "Lookonchain", "ArkhamIntel"], Config.RSS_FEEDS, False)

items_with_media = [item for item in items if item.get("has_media") and item.get("media_urls")]
print(f"Total items fetched: {len(items)}")
print(f"Items with images: {len(items_with_media)}")

publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)

# Test Telegram photo posting capabilities with a sample test photo URL
sample_photo_url = "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?w=800"
test_title = "<b>📸 PHOTO TEST: Crypto Bot Media Verification</b>"
test_text = "💥 <b>Media Verification</b>: Confirming that Telegram photo publishing and media rendering work 100% cleanly!"

print("\n=== 2. TESTING TELEGRAM SENDPHOTO FUNCTIONALITY ===")
res_channel, err = publisher.send_to_channel(test_title, test_text, has_media=True, media_urls=[sample_photo_url])
print(f"Photo post send_to_channel result: {res_channel} (Error: {err})")

res_admin = publisher.send_admin_preview(db_id=777, title=test_title, post_text=test_text, author="SystemTest", has_media=True, media_urls=[sample_photo_url])
print(f"Photo post send_admin_preview result: {res_admin}")
