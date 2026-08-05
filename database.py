import sqlite3
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("Database")

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
        except Exception:
            pass
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Track processed tweets/news items
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_tweets (
                    tweet_id TEXT PRIMARY KEY,
                    author TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT,
                    details TEXT
                )
            """)
            # Track pending posts for ADMIN_PREVIEW mode
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pending_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tweet_id TEXT,
                    author TEXT,
                    title TEXT,
                    post_text TEXT,
                    twitter_post TEXT DEFAULT '',
                    has_media INTEGER,
                    media_urls TEXT,
                    suggested_tags TEXT,
                    sniper_reply TEXT DEFAULT '',
                    target_platform TEXT DEFAULT 'BOTH',
                    ai_opinion TEXT DEFAULT '',
                    source_url TEXT DEFAULT '',
                    status TEXT DEFAULT 'PENDING',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Track LLM API cost & token consumption
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS llm_cost_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id TEXT,
                    model TEXT,
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    cost_usd REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Track published posts & telegram performance stats (views, forwards)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS published_posts_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pending_id INTEGER,
                    telegram_message_id INTEGER,
                    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    views_count INTEGER DEFAULT 0,
                    shares_count INTEGER DEFAULT 0
                )
            """)

            # Migrations check
            for col in [
                ("twitter_post", "TEXT DEFAULT ''"),
                ("twitter_thread", "TEXT DEFAULT '[]'"),
                ("sniper_reply", "TEXT DEFAULT ''"),
                ("target_platform", "TEXT DEFAULT 'BOTH'"),
                ("ai_opinion", "TEXT DEFAULT ''"),
                ("source_url", "TEXT DEFAULT ''")
            ]:
                try:
                    cursor.execute(f"ALTER TABLE pending_posts ADD COLUMN {col[0]} {col[1]}")
                except Exception:
                    pass

            conn.commit()

    def is_item_processed(self, item_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM processed_tweets WHERE tweet_id = ?", (str(item_id),))
            return cursor.fetchone() is not None

    def record_processed_item(self, item_id: str, author: str, status: str, details: str = ""):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO processed_tweets (tweet_id, author, status, details) VALUES (?, ?, ?, ?)",
                (str(item_id), author, status, details)
            )
            conn.commit()

    def save_pending_post(self, item_id: str, author: str, title: str, post_text: str,
                          has_media: bool, media_urls: list, suggested_tags: list,
                          twitter_post: str = "", sniper_reply: str = "", target_platform: str = "BOTH",
                          ai_opinion: str = "", source_url: str = "", twitter_thread: list = None) -> int:
        twitter_thread = twitter_thread or []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO pending_posts 
                (tweet_id, author, title, post_text, twitter_post, twitter_thread, has_media, media_urls, suggested_tags, sniper_reply, target_platform, ai_opinion, source_url, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
                """,
                (
                    str(item_id), author, title, post_text, twitter_post,
                    json.dumps(twitter_thread),
                    1 if has_media else 0,
                    json.dumps(media_urls),
                    json.dumps(suggested_tags),
                    sniper_reply,
                    target_platform,
                    ai_opinion,
                    source_url
                )
            )
            conn.commit()
            return cursor.lastrowid

    def get_pending_post(self, db_id: int) -> Optional[dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, tweet_id, author, title, post_text, twitter_post, has_media, media_urls, sniper_reply, target_platform, ai_opinion, source_url, status, twitter_thread
                FROM pending_posts WHERE id = ?
            """, (db_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "tweet_id": row[1],
                "author": row[2],
                "title": row[3],
                "post_text": row[4],
                "twitter_post": row[5] if len(row) > 5 and row[5] else "",
                "has_media": bool(row[6]),
                "media_urls": json.loads(row[7]) if row[7] else [],
                "sniper_reply": row[8] if len(row) > 8 and row[8] else "",
                "target_platform": row[9] if len(row) > 9 and row[9] else "BOTH",
                "ai_opinion": row[10] if len(row) > 10 and row[10] else "",
                "source_url": row[11] if len(row) > 11 and row[11] else "",
                "status": row[12] if len(row) > 12 else "PENDING",
                "twitter_thread": json.loads(row[13]) if len(row) > 13 and row[13] else []
            }

    def update_pending_post_status(self, db_id: int, status: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE pending_posts SET status = ? WHERE id = ?", (status, db_id))
            conn.commit()

    def update_pending_post_text(self, db_id: int, title: str, post_text: str):
        """Updates title and post_text of a pending post after AI re-editing."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE pending_posts SET title = ?, post_text = ? WHERE id = ?", (title, post_text, db_id))
            conn.commit()

    def log_llm_cost(self, item_id: str, model: str, prompt_tokens: int, completion_tokens: int, cost_usd: float):
        """Logs OpenRouter / DeepSeek token usage and estimated cost in USD."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO llm_cost_logs (item_id, model, prompt_tokens, completion_tokens, cost_usd)
                VALUES (?, ?, ?, ?, ?)
            """, (str(item_id), model, prompt_tokens, completion_tokens, cost_usd))
            conn.commit()

    def record_published_message(self, pending_id: int, telegram_message_id: int):
        """Records published Telegram message ID for performance and views tracking."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO published_posts_stats (pending_id, telegram_message_id, views_count)
                VALUES (?, ?, 0)
            """, (pending_id, telegram_message_id))
            conn.commit()

    def update_post_views(self, telegram_message_id: int, views_count: int):
        """Updates views count for a published Telegram message."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE published_posts_stats SET views_count = ? WHERE telegram_message_id = ?
            """, (views_count, telegram_message_id))
            conn.commit()

    def get_analytics_summary(self) -> dict:
        """Returns summarized performance metrics and unit economics ROI breakdown."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM pending_posts")
            total_items = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM pending_posts WHERE status = 'PUBLISHED'")
            published_items = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(cost_usd) FROM llm_cost_logs")
            total_cost_usd = cursor.fetchone()[0] or 0.0

            cursor.execute("SELECT SUM(views_count) FROM published_posts_stats")
            total_views = cursor.fetchone()[0] or 0

            avg_cost_per_post = (total_cost_usd / published_items) if published_items > 0 else 0.0

            return {
                "total_items": total_items,
                "published_items": published_items,
                "total_views": total_views,
                "total_cost_usd": round(total_cost_usd, 4),
                "avg_cost_per_post_usd": round(avg_cost_per_post, 4)
            }

    def get_recent_post_topics(self, limit: int = 30) -> list:
        """Retrieves recent post titles/summaries from pending_posts to prevent duplicate news coverage."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT title FROM pending_posts 
                WHERE status IN ('PENDING', 'PUBLISHED')
                ORDER BY created_at DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [r[0] for r in rows if r[0]]
