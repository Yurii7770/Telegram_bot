import sys
import io
import time
from config import Config
from database import Database
from telegram_publisher import TelegramPublisher

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def main():
    db = Database(Config.DATABASE_PATH)
    publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)

    item_id = f"demo_{int(time.time())}"
    author = "Lookonchain"
    title = "🚨 BREAKING: Whale Buys 12,450 $ETH ($41.2M) During Market Dip!"
    post_text = (
        "💥 A massive whale wallet just accumulated <b>12,450 $ETH</b> ($41.2M) across Binance and Uniswap V3 over the past 3 hours.\n\n"
        "📌 <b>Key On-Chain Metrics:</b>\n"
        "• <b>Avg Buying Price:</b> $3,310 per $ETH\n"
        "• <b>Wallet Balance:</b> Currently holding 45,800 $ETH ($151.6M total)\n"
        "• <b>Market Impact:</b> $ETH price rebounded +3.8% following the accumulation\n\n"
        "This institutional-scale buy indicates strong confidence at current support levels."
    )
    twitter_post = (
        "🚨 WHALE ALERT: Whale buys 12,450 $ETH ($41.2M) during dip!\n\n"
        "Avg entry: $3,310. Wallet now holds over 45.8K $ETH ($151.6M). $ETH ⚡"
    )
    sniper_reply = "💬 Massive $ETH accumulation by this whale! Institutional support at $3,310 looks solid."
    ai_opinion = "💡 Рекомендация ИИ: Сильный ончейн-сигнал покупки крупным китом. Рекомендуется опубликовать в Telegram и X!"
    source_url = "https://x.com/lookonchain/status/1880000000000000000"
    
    # High quality crypto image demo URL
    media_urls = ["https://pbs.twimg.com/media/GjL6934XwAAzJ5S?format=jpg&name=medium"]

    print("=== Saving pending post to DB ===")
    db_id = db.save_pending_post(
        item_id=item_id,
        author=author,
        title=title,
        post_text=post_text,
        has_media=True,
        media_urls=media_urls,
        suggested_tags=["ETH", "Lookonchain", "WhaleAlert"],
        twitter_post=twitter_post,
        sniper_reply=sniper_reply,
        target_platform="BOTH",
        ai_opinion=ai_opinion,
        source_url=source_url
    )

    print(f"=== Sending Demo Preview #{db_id} to Admin ({Config.ADMIN_CHAT_ID}) ===")
    success = publisher.send_admin_preview(
        db_id=db_id,
        title=title,
        post_text=post_text,
        author=author,
        has_media=True,
        media_urls=media_urls,
        twitter_post=twitter_post,
        sniper_reply=sniper_reply,
        target_platform="BOTH",
        ai_opinion=ai_opinion,
        source_url=source_url
    )

    if success:
        print(f"✅ Demo post #{db_id} successfully sent to Admin Telegram chat!")
    else:
        print(f"❌ Failed to send demo post to Admin Telegram chat.")

if __name__ == "__main__":
    main()
