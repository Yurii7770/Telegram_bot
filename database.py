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
        return sqlite3.connect(self.db_path)

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
            # Migrations check
            for col in [
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
                          sniper_reply: str = "", target_platform: str = "BOTH",
                          ai_opinion: str = "", source_url: str = "") -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO pending_posts 
                (tweet_id, author, title, post_text, has_media, media_urls, suggested_tags, sniper_reply, target_platform, ai_opinion, source_url, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
                """,
                (
                    str(item_id), author, title, post_text,
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
                SELECT id, tweet_id, author, title, post_text, has_media, media_urls, sniper_reply, target_platform, ai_opinion, source_url, status
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
                "has_media": bool(row[5]),
                "media_urls": json.loads(row[6]) if row[6] else [],
                "sniper_reply": row[7] if len(row) > 7 and row[7] else "",
                "target_platform": row[8] if len(row) > 8 and row[8] else "BOTH",
                "ai_opinion": row[9] if len(row) > 9 and row[9] else "",
                "source_url": row[10] if len(row) > 10 and row[10] else "",
                "status": row[11] if len(row) > 11 else "PENDING"
            }

    def update_pending_post_status(self, db_id: int, status: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE pending_posts SET status = ? WHERE id = ?", (status, db_id))
            conn.commit()

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
