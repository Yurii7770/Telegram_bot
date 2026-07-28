import sys
import io
from config import Config
from telegram_publisher import TelegramPublisher

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=== TESTING INSTANT TWITTER REPLY BUTTON & POSTER INTEGRATION ===")
publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)

title = "<b>⚡ JUST IN: DefiLlama Launches Real-Time Yield Tracker</b>"
post_text = "💥 <b>DefiLlama</b> unveiled a major real-time yield aggregator tracking 100+ L2 protocols."
sniper_reply = "🔥 Yield tracking across 100+ L2s is massive for DeFi liquidity. Game changer by DefiLlama."
ai_opinion = "💡 ИИ Рекомендация: Выкладываем пост в Telegram + обязательно жмем кнопку '🐦 В Twitter (Sniper)' для публикации ответа в течение 3-х минут."

sent = publisher.send_admin_preview(
    db_id=1010,
    title=title,
    post_text=post_text,
    author="DefiLlama",
    sniper_reply=sniper_reply,
    target_platform="BOTH",
    ai_opinion=ai_opinion
)

print(f"Admin preview sent to Telegram with [🐦 В Twitter (Sniper)] button: {sent}")
