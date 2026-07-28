import os
import logging
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenRouter API settings
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet").strip()
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip()

    # Telegram Bot Settings
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "").strip()

    # Publishing Mode: "DIRECT" or "ADMIN_PREVIEW"
    PUBLISH_MODE = os.getenv("PUBLISH_MODE", "ADMIN_PREVIEW").strip().upper()

    # Monitoring interval in minutes
    CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "15"))

    # Target Twitter accounts
    raw_accounts = os.getenv("TARGET_ACCOUNTS", "DuneAnalytics,DefiLlama,MessariCrypto,vitalikbuterin")
    TARGET_ACCOUNTS = [acc.strip().lstrip("@") for acc in raw_accounts.split(",") if acc.strip()]

    # Twitter authentication cookies (for Twikit)
    TWITTER_AUTH_TOKEN = os.getenv("TWITTER_AUTH_TOKEN", "").strip()
    TWITTER_CT0 = os.getenv("TWITTER_CT0", "").strip()
    TWITTER_TWID = os.getenv("TWITTER_TWID", "").strip()

    # RSS Crypto Feeds Fallback
    ENABLE_RSS_FEEDS = os.getenv("ENABLE_RSS_FEEDS", "false").strip().lower() == "true"
    RSS_FEEDS = [
        ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
        ("CoinTelegraph", "https://cointelegraph.com/rss"),
        ("Decrypt", "https://decrypt.co/feed")
    ]

    # Database
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_data.db")
