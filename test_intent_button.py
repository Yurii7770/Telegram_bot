from config import Config
from telegram_publisher import TelegramPublisher

publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)

print("=== Sending Admin Preview with 1-Click Twitter Intent URL button ===")
res = publisher.send_admin_preview(
    db_id=7777,
    title="🚨 <b>ТЕСТ 1-CLICK TWITTER SNIPER BUTTON</b>",
    post_text="💥 Бот сгенерировал кнопку '🚀 В Twitter (1-Click)' напрямую под постом!",
    author="vitalikbuterin",
    has_media=False,
    media_urls=[],
    sniper_reply="💬 Great insight by Vitalik! Scaling Ethereum is the key priority for 2026.",
    target_platform="BOTH",
    ai_opinion="💡 Нажмите на синюю кнопку под этим сообщением для отправки ответа в 1 клик!",
    source_url="https://x.com/vitalikbuterin/status/2082440000000000000"
)

print(f"Result: {res}")
