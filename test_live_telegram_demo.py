import sys
import os
import io
import time
import logging

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("LiveTelegramDemo")

from config import Config
from database import Database
from ai_editor import AIEditor
from telegram_publisher import TelegramPublisher

def main():
    logger.info("================================================================================")
    logger.info(" 🚀 STARTING LIVE TELEGRAM DEMO TEST FOR ADMIN PREVIEW & INTERACTIVE BUTTONS")
    logger.info("================================================================================")

    if not Config.TELEGRAM_BOT_TOKEN or not Config.ADMIN_CHAT_ID:
        logger.error("TELEGRAM_BOT_TOKEN or ADMIN_CHAT_ID is missing in .env! Cannot run live demo.")
        return

    db = Database(Config.DATABASE_PATH)
    ai_editor = AIEditor(
        openrouter_key=Config.OPENROUTER_API_KEY,
        model_name=Config.OPENROUTER_MODEL,
        base_url=Config.OPENROUTER_BASE_URL
    )
    publisher = TelegramPublisher(
        bot_token=Config.TELEGRAM_BOT_TOKEN,
        channel_chat_id=Config.TELEGRAM_CHAT_ID,
        admin_chat_id=Config.ADMIN_CHAT_ID
    )

    # 1. Start background listener for Telegram buttons and /stats command
    publisher.start_callback_listener(db)
    logger.info(f"Telegram listener active for admin ID: {Config.ADMIN_CHAT_ID}")

    # 2. Prepare high-quality mock crypto item with media photo
    test_item = {
        "id": f"demo_item_{int(time.time())}",
        "author": "Lookonchain",
        "title": "🚨 WHALE ALERT: 12,500 ETH Deposited to Binance & Bybit",
        "text": "Whale 0x7a3f deposited 12,500 ETH ($38.5M) into Binance and Bybit 15 minutes ago. Volume on Uniswap and DexScreener surged by 140%.",
        "url": "https://x.com/Lookonchain/status/1880000000000000000",
        "has_media": True,
        "media_urls": ["https://images.unsplash.com/photo-1621416894569-0f39ed31d247?w=800&auto=format&fit=crop"]
    }

    logger.info("Processing demo item through AI Editor...")
    ai_res = ai_editor.process_item(test_item, recent_topics=[])

    # Fallback if AI fails or returns empty
    title = ai_res.get("title") or "🚨 <b>WHALE ALERT:</b> Arkham Tracks <a href='https://x.com'>$38.5M ETH Transfer</a>!"
    post_text = ai_res.get("post_text") or (
        "💥 <b>Lookonchain</b> detected a major whale movement of 12,500 ETH ($38.5M) sent to <b>Bybit</b> and <b>Binance</b>.\n\n"
        "📌 <b>Key On-Chain Metrics:</b>\n"
        "• <b>Volume Surge:</b> +140% trading activity recorded on <b>Uniswap</b> and <b>DexScreener</b>.\n"
        "• <b>Whale Address:</b> 0x7a3f...89e2 (Profit on trade: +$4.2M).\n\n"
        "Market sentiment remains highly bullish as liquidity shifts across DEX protocols."
    )
    twitter_post = ai_res.get("twitter_post") or "🚨 WHALE ALERT: 12,500 ETH ($38.5M) moved to Bybit & Binance! Trading volume spikes +140%. $ETH ⚡"
    sniper_reply = ai_res.get("sniper_reply") or "💬 Massive ETH liquidity inflow. Watching on-chain exchange reserves closely. $ETH"
    target_platform = ai_res.get("target_platform", "BOTH")
    ai_opinion = ai_res.get("ai_opinion") or "💡 <b>Рекомендация ИИ:</b> Отличная инсайд-новость с ончейн-данными. Публикуем в Telegram и Twitter!"
    source_url = test_item["url"]
    media_urls = test_item["media_urls"]

    # 3. Log simulated LLM cost
    db.log_llm_cost(test_item["id"], Config.OPENROUTER_MODEL, 450, 180, 0.00095)

    # 4. Save pending post to DB
    db_id = db.save_pending_post(
        item_id=test_item["id"],
        author=test_item["author"],
        title=title,
        post_text=post_text,
        has_media=True,
        media_urls=media_urls,
        suggested_tags=["#WhaleAlert", "#Ethereum"],
        twitter_post=twitter_post,
        sniper_reply=sniper_reply,
        target_platform=target_platform,
        ai_opinion=ai_opinion,
        source_url=source_url
    )

    logger.info(f"Saved pending demo post #{db_id} to database. Sending preview to Telegram Admin ({Config.ADMIN_CHAT_ID})...")

    # 5. Send preview to Telegram Admin (with image download & automatic watermark overlay!)
    success = publisher.send_admin_preview(
        db_id=db_id,
        title=title,
        post_text=post_text,
        author=test_item["author"],
        has_media=True,
        media_urls=media_urls,
        twitter_post=twitter_post,
        sniper_reply=sniper_reply,
        target_platform=target_platform,
        ai_opinion=ai_opinion,
        source_url=source_url
    )

    if success:
        logger.info("================================================================================")
        logger.info(" ✅ DEMO POST SUCCESSFULLY SENT TO YOUR TELEGRAM ADMIN CHAT!")
        logger.info(" ================================================================================")
        logger.info("📱 Проверьте Telegram! Вам пришло превью поста с:")
        logger.info("  1. 🖼 Фотографией с НАЛОЖЕННЫМ ВОДЯНЫМ ЗНАКОМ (@CryptoChannel)")
        logger.info("  2. 🔗 Вшитыми партнерскими ссылками (Bybit, Uniswap, DexScreener)")
        logger.info("  3. ⚡ Кнопками ИИ-редактирования: [✂️ Укоротить], [🔥 Хайп], [🌐 Перевести], [🔄 Рерайт]")
        logger.info("  4. 📊 Попробуйте также отправить боту команду /stats в Telegram!")
        logger.info("--------------------------------------------------------------------------------")
        logger.info("Слушатель кнопок активен. Нажимайте кнопки в Telegram для тестирования...")
        
        # Keep listener alive for 2 minutes so user can click interactive buttons
        try:
            for i in range(120, 0, -10):
                logger.info(f"⏳ Ожидание кликов администратора в Telegram ({i} сек оставшиеся)...")
                time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Demo listener stopped.")
    else:
        logger.error("❌ Failed to send admin preview to Telegram. Check bot token and admin chat ID.")

if __name__ == "__main__":
    main()
