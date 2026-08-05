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

    item_id = f"demo_thread_{int(time.time())}"
    author = "DefiLlama"
    title = "🚨 BREAKING: Solana Ecosystem TVL Surges Past $5.2B as DePIN Volume Skyrockets!"
    post_text = (
        "💥 <b>Solana Ecosystem</b> total value locked (TVL) has broken past $5.2B, recording a +24% gain over the last 7 days.\n\n"
        "📌 <b>Key On-Chain Metrics:</b>\n"
        "• <b>TVL ATH:</b> $5.2B reached driven by Jupiter and Raydium DEX volume\n"
        "• <b>Active Wallets:</b> Daily active addresses hit new ATH at 1.8M\n"
        "• <b>Token Impact:</b> $SOL touches $185 resistance level with massive spot volume"
    )
    twitter_post = (
        "🚨 BREAKING: Solana TVL surges past $5.2B (+24% in 7 days)! $SOL ⚡"
    )
    twitter_thread = [
        "1/4 🚨 BREAKING: Solana Ecosystem TVL has broken past $5.2B, recording a massive +24% gain over the last 7 days! $SOL ⚡",
        "2/4 📊 On-Chain Data: DEX volume on Jupiter & Raydium pushed daily active addresses to a new ATH of 1.8M active wallets.",
        "3/4 🐋 Market Impact: Spot buying pressure pushed $SOL to test $185 resistance with institutional volume surges.",
        "4/4 🧵 Full live wallet flow breakdowns & real-time alerts live on @CRETH 🎯"
    ]
    sniper_reply = "👀 Notice how DePIN volume surged 300% right before this TVL breakout? Full wallet cluster breakdown live on @CRETH 🎯"
    ai_opinion = "💡 Рекомендация ИИ: Отличный трендовый повод. Публикуем в Telegram и отправляем аналитический тред в X!"
    source_url = "https://x.com/DefiLlama/status/1890000000000000000"
    media_urls = ["https://pbs.twimg.com/media/GjL6934XwAAzJ5S?format=jpg&name=medium"]

    print("=== Saving pending thread post to DB ===")
    db_id = db.save_pending_post(
        item_id=item_id,
        author=author,
        title=title,
        post_text=post_text,
        has_media=True,
        media_urls=media_urls,
        suggested_tags=["Solana", "TVL", "DefiLlama"],
        twitter_post=twitter_post,
        sniper_reply=sniper_reply,
        target_platform="BOTH",
        ai_opinion=ai_opinion,
        source_url=source_url,
        twitter_thread=twitter_thread
    )

    print(f"=== Sending Demo Thread Preview #{db_id} to Admin ({Config.ADMIN_CHAT_ID}) ===")
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
        print(f"✅ Demo thread post #{db_id} successfully sent to Admin Telegram chat!")
    else:
        print(f"❌ Failed to send demo thread post to Admin Telegram chat.")

if __name__ == "__main__":
    main()
