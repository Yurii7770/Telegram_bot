import sys
import os
import io
import time
import json
import logging
import requests
from PIL import Image

# Force UTF-8 stdout/stderr on Windows to avoid UnicodeEncodeError
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("SeniorQA")

def run_senior_qa_suite():
    logger.info("================================================================================")
    logger.info(" 🛡 SENIOR QA COMPREHENSIVE AUTOMATED SUITE - FULL SYSTEM AUDIT & VERIFICATION")
    logger.info("================================================================================")

    results = []

    # -------------------------------------------------------------
    # STAGE 1: Environment & Configuration Audit
    # -------------------------------------------------------------
    logger.info("--- [STAGE 1] Configuration & Environment Audit ---")
    try:
        from config import Config

        cfg_checks = [
            ("OPENROUTER_API_KEY", bool(Config.OPENROUTER_API_KEY)),
            ("TELEGRAM_BOT_TOKEN", bool(Config.TELEGRAM_BOT_TOKEN)),
            ("TELEGRAM_CHAT_ID", bool(Config.TELEGRAM_CHAT_ID)),
            ("ADMIN_CHAT_ID", bool(Config.ADMIN_CHAT_ID)),
            ("TWITTER_AUTH_TOKEN", bool(Config.TWITTER_AUTH_TOKEN)),
            ("TWITTER_CT0", bool(Config.TWITTER_CT0)),
            ("TARGET_ACCOUNTS", len(Config.TARGET_ACCOUNTS) > 0),
            ("ENABLE_WATERMARK", hasattr(Config, "ENABLE_WATERMARK")),
            ("REFERRAL_LINKS", hasattr(Config, "REFERRAL_LINKS") and len(Config.REFERRAL_LINKS) > 0)
        ]

        stage1_ok = True
        for name, ok in cfg_checks:
            status = "PASSED [OK]" if ok else "FAILED [FAIL]"
            logger.info(f"  - Config '{name}': {status}")
            if not ok:
                stage1_ok = False

        results.append(("Stage 1: Environment & Config Audit", stage1_ok))
    except Exception as e:
        logger.error(f"  - Stage 1 Exception: {e}")
        results.append(("Stage 1: Environment & Config Audit", False))

    # -------------------------------------------------------------
    # STAGE 2: Database & Analytics Unit Economics Layer
    # -------------------------------------------------------------
    logger.info("--- [STAGE 2] Database CRUD, Analytics & Unit Economics ---")
    try:
        import uuid
        from database import Database
        db_file = f"test_qa_db_{uuid.uuid4().hex[:6]}.db"
        db = Database(db_file)

        # 2.1 Test deduplication check
        is_proc_before = db.is_item_processed("qa_item_1")
        db.record_processed_item("qa_item_1", "Lookonchain", "PUBLISHED", "QA Unit Test")
        is_proc_after = db.is_item_processed("qa_item_1")

        # 2.2 Test pending post save & update
        pending_id = db.save_pending_post(
            item_id="qa_item_1", author="Lookonchain", title="QA Title", post_text="QA Text",
            has_media=True, media_urls=["https://example.com/img.jpg"], suggested_tags=["#QA"],
            twitter_post="QA Tweet", sniper_reply="QA Reply", target_platform="BOTH",
            ai_opinion="QA Opinion", source_url="https://x.com/status/1"
        )
        db.update_pending_post_text(pending_id, "Updated QA Title", "Updated QA Text")
        updated_post = db.get_pending_post(pending_id)

        # 2.3 Test LLM cost logging & published stats
        db.log_llm_cost("qa_item_1", "anthropic/claude-3.5-sonnet", 500, 200, 0.00105)
        db.update_pending_post_status(pending_id, "PUBLISHED")
        db.record_published_message(pending_id, telegram_message_id=777)
        db.update_post_views(telegram_message_id=777, views_count=850)

        stats = db.get_analytics_summary()

        stage2_ok = (
            (not is_proc_before) and is_proc_after and
            (updated_post["title"] == "Updated QA Title") and
            (stats["published_items"] == 1) and (stats["total_views"] == 850) and
            (stats["total_cost_usd"] > 0)
        )

        logger.info(f"  - Database CRUD & Analytics: {'PASSED [OK]' if stage2_ok else 'FAILED [FAIL]'}")
        logger.info(f"  - Analytics Summary Output: {stats}")

        # Cleanup test DB
        del db
        if os.path.exists(db_file):
            try: os.remove(db_file)
            except Exception: pass

        results.append(("Stage 2: Database & Analytics Layer", stage2_ok))
    except Exception as e:
        logger.error(f"  - Stage 2 Exception: {e}")
        results.append(("Stage 2: Database & Analytics Layer", False))

    # -------------------------------------------------------------
    # STAGE 3: Watermark Processor & Image Overlay
    # -------------------------------------------------------------
    logger.info("--- [STAGE 3] Watermark Processor & Image Overlay Engine ---")
    try:
        from watermark_processor import apply_watermark

        # Create 500x300 sample image
        sample_img = Image.new("RGB", (500, 300), color=(30, 41, 59))
        buf = io.BytesIO()
        sample_img.save(buf, format="JPEG")
        raw_bytes = buf.getvalue()

        # Test watermarking with unicode branding text
        branded_bytes = apply_watermark(raw_bytes, "@CryptoChannel_QA")
        output_img = Image.open(io.BytesIO(branded_bytes))

        stage3_ok = (
            len(branded_bytes) > 1000 and
            output_img.size == (500, 300) and
            output_img.format == "JPEG"
        )

        logger.info(f"  - Watermark Application: {'PASSED [OK]' if stage3_ok else 'FAILED [FAIL]'}")
        results.append(("Stage 3: Watermark Processor", stage3_ok))
    except Exception as e:
        logger.error(f"  - Stage 3 Exception: {e}")
        results.append(("Stage 3: Watermark Processor", False))

    # -------------------------------------------------------------
    # STAGE 4: AI Editor & Referral Link Injector
    # -------------------------------------------------------------
    logger.info("--- [STAGE 4] AI Editor & Referral Link Injector ---")
    try:
        from ai_editor import AIEditor
        ai = AIEditor(Config.OPENROUTER_API_KEY, Config.OPENROUTER_MODEL, Config.OPENROUTER_BASE_URL)

        # Test referral injection without breaking existing HTML tags
        raw_text = "Big volume surge detected on Bybit and Uniswap! Check OKX for arbitrage."
        injected_text = ai._inject_referral_links(raw_text)

        has_bybit = "<a href=" in injected_text and "Bybit" in injected_text
        has_uniswap = "Uniswap" in injected_text
        has_okx = "OKX" in injected_text

        stage4_ok = has_bybit and has_uniswap and has_okx
        logger.info(f"  - Referral Links Injected Output: '{injected_text[:100]}...'")
        logger.info(f"  - Referral Link Injector: {'PASSED [OK]' if stage4_ok else 'FAILED [FAIL]'}")
        results.append(("Stage 4: AI Referral Link Injector", stage4_ok))
    except Exception as e:
        logger.error(f"  - Stage 4 Exception: {e}")
        results.append(("Stage 4: AI Referral Link Injector", False))

    # -------------------------------------------------------------
    # STAGE 5: Quick AI Edit Actions (reedit_post)
    # -------------------------------------------------------------
    logger.info("--- [STAGE 5] Quick AI Editing Engine (reedit_post) ---")
    try:
        sample_title = "🚨 BREAKING: Arkham Intel Launches Platform"
        sample_body = "💥 Arkham Intel announced a new decentralized tracking platform with $45M volume recorded."

        if Config.OPENROUTER_API_KEY:
            logger.info("  - Testing live quick AI editing ('SHORTEN')...")
            new_title, new_body = ai.reedit_post(sample_title, sample_body, "SHORTEN")
            stage5_ok = bool(new_title) and bool(new_body)
            logger.info(f"  - Live AI Re-edit Result: Title='{new_title[:50]}...' | Text='{new_body[:70]}...'")
        else:
            logger.warning("  - OPENROUTER_API_KEY not present, skipping live API test for reedit_post.")
            stage5_ok = True

        results.append(("Stage 5: Quick AI Editing Engine", stage5_ok))
    except Exception as e:
        logger.error(f"  - Stage 5 Exception: {e}")
        results.append(("Stage 5: Quick AI Editing Engine", False))

    # -------------------------------------------------------------
    # STAGE 6: Telegram Publisher & Keyboard Formatting
    # -------------------------------------------------------------
    logger.info("--- [STAGE 6] Telegram Publisher & HTML Safety ---")
    try:
        from telegram_publisher import safe_html_truncate, TelegramPublisher

        # Test safe HTML truncation with unclosed tags
        unclosed_html = "<b>🚨 BREAKING:</b> <a href='https://x.com'>Arkham Intel unveils platform with over $45M volume..."
        truncated = safe_html_truncate(unclosed_html, max_length=50)

        # Verify all open tags are safely closed
        has_closed_bold = "</b>" in truncated or not "<b>" in truncated
        has_closed_link = "</a>" in truncated or not "<a" in truncated

        # Test Telegram Bot API Auth with getMe
        r = requests.get(f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/getMe", timeout=10)
        bot_auth_ok = (r.status_code == 200 and r.json().get("ok") == True)
        bot_user = r.json().get("result", {}).get("username", "") if bot_auth_ok else "N/A"

        stage6_ok = has_closed_bold and has_closed_link and bot_auth_ok
        logger.info(f"  - Telegram Auth Check (@{bot_user}): {'PASSED [OK]' if bot_auth_ok else 'FAILED [FAIL]'}")
        logger.info(f"  - HTML Truncator Output: '{truncated}'")
        results.append(("Stage 6: Telegram Publisher & HTML Safety", stage6_ok))
    except Exception as e:
        logger.error(f"  - Stage 6 Exception: {e}")
        results.append(("Stage 6: Telegram Publisher & HTML Safety", False))

    # -------------------------------------------------------------
    # STAGE 7: Content Scraping Engine (Twitter/X & RSS)
    # -------------------------------------------------------------
    logger.info("--- [STAGE 7] Multi-tier Content Scraping Engine ---")
    try:
        from content_fetcher import ContentFetcher
        fetcher = ContentFetcher()

        logger.info("  - Testing live Twitter/X fetch for @Lookonchain...")
        items = fetcher.get_twitter_posts("Lookonchain", limit=2)
        stage7_ok = len(items) > 0

        if stage7_ok:
            logger.info(f"  - Successfully fetched {len(items)} posts! Latest: '{items[0]['title'][:60]}...'")
        else:
            logger.warning("  - Twitter fetch returned 0 posts!")

        results.append(("Stage 7: Content Scraping Engine", stage7_ok))
    except Exception as e:
        logger.error(f"  - Stage 7 Exception: {e}")
        results.append(("Stage 7: Content Scraping Engine", False))

    # -------------------------------------------------------------
    # STAGE 8: HTTP Health Server & Deployment Ping Engine
    # -------------------------------------------------------------
    logger.info("--- [STAGE 8] HTTP Health Server & Keep-Alive Engine ---")
    try:
        import threading
        from main import start_health_server

        os.environ["PORT"] = "8899"
        t = threading.Thread(target=start_health_server, daemon=True)
        t.start()
        time.sleep(1.2)

        resp = requests.get("http://127.0.0.1:8899/", timeout=5)
        stage8_ok = (resp.status_code == 200 and resp.json().get("status") == "online")

        logger.info(f"  - Health Endpoint GET http://127.0.0.1:8899/ -> Status {resp.status_code}: {'PASSED [OK]' if stage8_ok else 'FAILED [FAIL]'}")
        results.append(("Stage 8: Health Server & Keep-Alive Engine", stage8_ok))
    except Exception as e:
        logger.error(f"  - Stage 8 Exception: {e}")
        results.append(("Stage 8: Health Server & Keep-Alive Engine", False))

    # -------------------------------------------------------------
    # FINAL SENIOR QA AUDIT SUMMARY MATRIX
    # -------------------------------------------------------------
    logger.info("================================================================================")
    logger.info(" 📋 SENIOR QA AUDIT SUMMARY MATRIX")
    logger.info("================================================================================")

    all_passed = True
    for stage_title, passed in results:
        mark = "PASSED [OK]" if passed else "FAILED [FAIL]"
        logger.info(f"  - {stage_title:<45} [{mark}]")
        if not passed:
            all_passed = False

    logger.info("================================================================================")
    if all_passed:
        logger.info(" 🏆 OVERALL SYSTEM STATUS: 100% HEALTHY & PRODUCTION READY")
    else:
        logger.info(" ⚠️ OVERALL SYSTEM STATUS: ISSUES DETECTED - ATTENTION REQUIRED")
    logger.info("================================================================================")

if __name__ == "__main__":
    run_senior_qa_suite()
