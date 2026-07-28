import sys
import io
from config import Config
from telegram_publisher import TelegramPublisher

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=== TESTING EXPLICIT SOURCE URL LINK IN TELEGRAM ADMIN PREVIEW ===")
publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)

title = "🚨 BREAKING: Vitalik Buterin <a href='https://x.com/vitalikbuterin/status/189999999999'>Outlines L2 Roadmap</a>"
post_text = "💥 <b>Vitalik Buterin</b> published an updated architectural vision focusing on trustless cross-L2 messaging."
sniper_reply = "🔥 Cross-L2 messaging is the missing piece for Ethereum UX. Huge roadmap update by Vitalik."
ai_opinion = "💡 ИИ Рекомендация: Пост для Telegram + быстрый Sniper Reply в X."
source_url = "https://x.com/vitalikbuterin/status/189999999999"

sent = publisher.send_admin_preview(
    db_id=1212,
    title=title,
    post_text=post_text,
    author="vitalikbuterin",
    sniper_reply=sniper_reply,
    target_platform="BOTH",
    ai_opinion=ai_opinion,
    source_url=source_url
)

print(f"Admin preview with explicit source URL sent: {sent}")
