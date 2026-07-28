import sys
import io
from config import Config
from telegram_publisher import TelegramPublisher

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)

sample_photo_url = "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?w=800"
title = "<b>📸 PHOTO PREVIEW TEST: Admin Preview With Image</b>"
post_text = "💥 <b>Image Verification</b>: Confirming that photos are rendered directly inside Telegram Admin Previews with inline buttons and Sniper Reply box!"
sniper_reply = "🔥 High-resolution visual confirmation. Fully verified."

print("=== Testing Admin Photo Preview Send ===")
sent = publisher.send_admin_preview(
    db_id=888,
    title=title,
    post_text=post_text,
    author="DefiLlama",
    has_media=True,
    media_urls=[sample_photo_url],
    sniper_reply=sniper_reply
)

print(f"Photo admin preview result: {sent}")
