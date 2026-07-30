import os
import time
import sys
import io
import logging
import argparse
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Force UTF-8 stdout/stderr on Windows to avoid UnicodeEncodeError (cp1251)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from config import Config
from database import Database
from ai_editor import AIEditor
from content_fetcher import ContentFetcher
from telegram_publisher import TelegramPublisher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("CryptoBot")

# Lightweight HTTP Health Check server for FREE deployment on Render / Cloud Web Services
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        response_data = {
            "status": "online",
            "service": "Crypto Telegram AI Bot",
            "check_interval_minutes": Config.CHECK_INTERVAL_MINUTES,
            "target_accounts_count": len(Config.TARGET_ACCOUNTS),
            "timestamp": time.time()
        }
        import json
        self.wfile.write(json.dumps(response_data, indent=2).encode('utf-8'))

    def log_message(self, format, *args):
        pass  # Silence HTTP server logs

def start_health_server():
    port = int(os.getenv("PORT", "8080"))
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        logger.info(f"Health check HTTP server listening on 0.0.0.0:{port}")
        server.serve_forever()
    except Exception as e:
        logger.warning(f"Health server failed to start: {e}")

def start_keep_alive_pinger():
    """Background thread that pings Render's external URL every 5 minutes to keep the web service awake 24/7."""
    time.sleep(15)  # Wait for health server to start
    url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("APP_URL") or os.getenv("KEEP_ALIVE_URL")
    if not url:
        port = os.getenv("PORT", "8080")
        url = f"http://127.0.0.1:{port}"
        logger.info(f"Keep-Alive: No public RENDER_EXTERNAL_URL found, defaulting to internal endpoint {url}")
    else:
        logger.info(f"Keep-Alive: Public URL detected -> {url}")

    ping_interval_sec = 300  # 5 minutes
    import requests

    while True:
        try:
            resp = requests.get(url, timeout=15)
            logger.info(f"[Keep-Alive Ping] Sent GET to {url} - Status: {resp.status_code}")
        except Exception as e:
            logger.warning(f"[Keep-Alive Ping] Error pinging {url}: {e}")
        time.sleep(ping_interval_sec)

class BotDaemon:
    def __init__(self):
        self.db = Database(Config.DATABASE_PATH)
        self.ai_editor = AIEditor(
            openrouter_key=Config.OPENROUTER_API_KEY,
            model_name=Config.OPENROUTER_MODEL,
            base_url=Config.OPENROUTER_BASE_URL
        )
        self.fetcher = ContentFetcher(Config.TWITTER_AUTH_TOKEN, Config.TWITTER_CT0)
        self.publisher = TelegramPublisher(
            bot_token=Config.TELEGRAM_BOT_TOKEN,
            channel_chat_id=Config.TELEGRAM_CHAT_ID,
            admin_chat_id=Config.ADMIN_CHAT_ID
        )
        # Start background listener for inline moderation buttons (Publish / Reject)
        self.publisher.start_callback_listener(self.db)

    def run_check_cycle(self):
        logger.info("=== Starting content check cycle ===")
        items = self.fetcher.fetch_all_sources(
            twitter_accounts=Config.TARGET_ACCOUNTS,
            rss_feeds=Config.RSS_FEEDS,
            enable_rss=Config.ENABLE_RSS_FEEDS
        )

        if not items:
            logger.warning("No items fetched from any sources.")
            return

        new_count = 0
        published_count = 0
        max_batch_per_cycle = 5  # Max items to process per cycle to prevent OpenRouter rate limits

        for item in items:
            if new_count >= max_batch_per_cycle:
                logger.info(f"Reached cycle processing cap ({max_batch_per_cycle} items). Remaining items will be processed in next cycle.")
                break

            item_id = item["id"]
            if self.db.is_item_processed(item_id):
                continue

            new_count += 1
            author = item["author"]
            logger.info(f"Processing new item [{item_id}] from @{author}: '{item['title'][:60]}...'")

            # Fetch recent topics to prevent duplicate posts on the same event
            recent_topics = self.db.get_recent_post_topics(limit=30)
            # Process through AI Editor with deduplication check
            ai_result = self.ai_editor.process_item(item, recent_topics=recent_topics)
            status = ai_result.get("status", "SKIP")

            if status == "ERROR" or "error" in ai_result.get("reason", "").lower() or "empty" in ai_result.get("reason", "").lower() or "json" in ai_result.get("reason", "").lower():
                reason = ai_result.get("reason", "API Error")
                logger.warning(f"Item [{item_id}] failed due to AI error: {reason}. Skipping DB recording so it can be retried next cycle.")
                time.sleep(2)
                continue

            if status == "SKIP":
                reason = ai_result.get("reason", "Filtered by AI rules")
                logger.info(f"Item [{item_id}] skipped by AI. Reason: {reason}")
                self.db.record_processed_item(item_id, author, "SKIP", reason)
                time.sleep(1)
                continue

            # Item passed AI rules!
            title = ai_result.get("title", "")
            post_text = ai_result.get("post_text", "")
            suggested_tags = ai_result.get("suggested_tags", [])
            sniper_reply = ai_result.get("sniper_reply", "")
            target_platform = ai_result.get("target_platform", "BOTH")
            ai_opinion = ai_result.get("ai_opinion", "")
            source_url = item.get("url", "")
            has_media = item.get("has_media", False)
            media_urls = item.get("media_urls", [])

            if Config.PUBLISH_MODE == "DIRECT":
                success, _ = self.publisher.send_to_channel(title, post_text, has_media, media_urls)
                if success:
                    published_count += 1
                    self.db.record_processed_item(item_id, author, "PUBLISHED", "Published to channel")
                else:
                    self.db.record_processed_item(item_id, author, "FAILED", "Telegram publish error")
            else:
                # ADMIN_PREVIEW mode
                db_id = self.db.save_pending_post(
                    item_id, author, title, post_text, has_media, media_urls,
                    suggested_tags, sniper_reply, target_platform, ai_opinion, source_url
                )
                success = self.publisher.send_admin_preview(
                    db_id, title, post_text, author, has_media, media_urls,
                    sniper_reply, target_platform, ai_opinion, source_url
                )
                if success:
                    published_count += 1
                    self.db.record_processed_item(item_id, author, "PENDING_ADMIN", f"Sent to admin preview #{db_id}")
                else:
                    self.db.record_processed_item(item_id, author, "FAILED", "Telegram admin preview error")

            time.sleep(1.5)  # Friendly delay between OpenRouter API requests

        logger.info(f"Cycle completed. Processed new items: {new_count}, Successfully sent: {published_count}")

def main():
    parser = argparse.ArgumentParser(description="Crypto Telegram AI Bot Daemon")
    parser.add_argument("--once", action="store_true", help="Run 1 check cycle immediately and exit")
    args = parser.parse_args()

    daemon = BotDaemon()

    if args.once:
        logger.info("Executing single diagnostic run (--once)...")
        daemon.run_check_cycle()
        sys.exit(0)

    # Start health check server in background thread for cloud deployment
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    # Start keep-alive pinger thread to prevent Render free tier spin-down / sleep mode
    pinger_thread = threading.Thread(target=start_keep_alive_pinger, daemon=True)
    pinger_thread.start()

    interval_sec = Config.CHECK_INTERVAL_MINUTES * 60
    logger.info(f"Bot daemon started. Polling interval: {Config.CHECK_INTERVAL_MINUTES} minutes ({interval_sec} seconds).")

    while True:
        try:
            daemon.run_check_cycle()
        except Exception as e:
            logger.error(f"Unhandled error in bot main loop: {e}", exc_info=True)

        logger.info(f"Sleeping for {Config.CHECK_INTERVAL_MINUTES} minutes...")
        time.sleep(interval_sec)

if __name__ == "__main__":
    main()
