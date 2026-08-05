import sys
import io
import os
import logging
from config import Config
from database import Database
from telegram_publisher import TelegramPublisher

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("TestPubX")

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def main():
    db = Database(Config.DATABASE_PATH)
    publisher = TelegramPublisher(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID, Config.ADMIN_CHAT_ID)

    post_id = 187
    post = db.get_pending_post(post_id)
    if not post:
        logger.error(f"Post #{post_id} not found!")
        return
    logger.info(f"Testing _async_process_pub_x for post #{post_id}...")

    # Execute worker method synchronously for testing
    publisher._async_process_pub_x(post_id=post_id, chat_id=int(Config.ADMIN_CHAT_ID), msg_id=0, db=db)

if __name__ == "__main__":
    main()
