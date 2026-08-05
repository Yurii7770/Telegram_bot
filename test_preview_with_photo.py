import requests
from config import Config
from telegram_publisher import TelegramPublisher

print("=== Testing TelegramPublisher with live image bytes upload ===")

publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)

# Use a valid public image URL to verify bytes upload
test_image_url = "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?w=600&auto=format&fit=crop"

success = publisher.send_admin_preview(
    db_id=9999,
    title="⚡ <b>ТЕСТОВАЯ ПУБЛИКАЦИЯ С КАРТИНКОЙ</b>",
    post_text="💥 Бот успешно скачивает картинку и загружает её в Telegram через multipart upload!",
    author="DefiLlama",
    has_media=True,
    media_urls=[test_image_url],
    sniper_reply="💬 Great update! Tracking TVL.",
    target_platform="BOTH",
    ai_opinion="💡 Рекомендуется выложить пост с картинкой в Telegram.",
    source_url="https://x.com/DefiLlama/status/2082280704495300824"
)

print(f"send_admin_preview result: {success}")
