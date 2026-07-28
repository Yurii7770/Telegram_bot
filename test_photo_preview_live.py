import sys
import io
from config import Config
from telegram_publisher import TelegramPublisher

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=== TESTING TELEGRAM PHOTO PREVIEW DELIVERY ===")
publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)

title = "🚨 BREAKING: Vitalik Buterin <a href='https://x.com/vitalikbuterin/status/2082132765886108082'>Unveils Obfuscation Part II</a>"
post_text = "💥 <b>Vitalik Buterin</b> published an in-depth technical analysis on diamond IO obfuscation and cryptographic proofs."
sniper_reply = "🔥 Cryptographic obfuscation is the next frontier for L1 privacy and scalability. Essential read."
ai_opinion = "💡 ИИ Рекомендация: Пост для Telegram + Sniper Reply в X."
source_url = "https://x.com/vitalikbuterin/status/2082132765886108082"
photo_url = "https://pbs.twimg.com/media/GfXxxxxW0AAxxxx?format=jpg&name=large"

sent = publisher.send_admin_preview(
    db_id=1500,
    title=title,
    post_text=post_text,
    author="vitalikbuterin",
    has_media=True,
    media_urls=[photo_url],
    sniper_reply=sniper_reply,
    target_platform="BOTH",
    ai_opinion=ai_opinion,
    source_url=source_url
)

print(f"Photo admin preview sent: {sent}")
