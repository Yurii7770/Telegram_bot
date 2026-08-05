from config import Config
from telegram_publisher import TelegramPublisher

publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)

print("=== Testing 3-Variation Inline Publishing Buttons in Telegram ===")
res = publisher.send_admin_preview(
    db_id=5555,
    title="⚡ <b>ТРЕХВАРИАНТНАЯ ПУБЛИКАЦИЯ</b>",
    post_text="💥 Бот подготовил три варианта публикации: в Telegram канал, новым постом в Twitter или реплаем!",
    author="MessariCrypto",
    has_media=False,
    media_urls=[],
    sniper_reply="💬 Great analysis by Messari on DeFi protocol revenues!",
    target_platform="BOTH",
    ai_opinion="💡 Рекомендуется опубликовать в TG и сделать реплай в Twitter.",
    source_url="https://x.com/MessariCrypto/status/2082440000000000000"
)

print(f"send_admin_preview result: {res}")
