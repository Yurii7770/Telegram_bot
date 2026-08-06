import logging
import requests
import json
import re
import io
import os
import time
import tempfile
import threading
import urllib.parse
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("TelegramPublisher")

def close_unclosed_tags(html_text: str) -> str:
    """Closes any open HTML tags in order of appearance."""
    tag_regex = re.compile(r'</?([a-zA-Z1-6]+)(?:\s+[^>]*)?>')
    stack = []
    for match in tag_regex.finditer(html_text):
        tag_str = match.group(0)
        tag_name = match.group(1).lower()
        if tag_name in ['br', 'img', 'hr', 'input']:
            continue
        if tag_str.startswith('</'):
            if stack and stack[-1] == tag_name:
                stack.pop()
            elif tag_name in stack:
                while stack and stack[-1] != tag_name:
                    stack.pop()
                if stack:
                    stack.pop()
        else:
            stack.append(tag_name)
    closing_tags = "".join(f"</{tag}>" for tag in reversed(stack))
    return html_text + closing_tags

def safe_html_truncate(html_text: str, max_length: int = 950) -> str:
    """Safely truncates an HTML string without cutting HTML tags, closing any unclosed tags."""
    if not html_text:
        return ""
    if len(html_text) <= max_length:
        return close_unclosed_tags(html_text)
    truncated = html_text[:max_length]
    last_open = truncated.rfind('<')
    last_close = truncated.rfind('>')
    if last_open > last_close:
        truncated = truncated[:last_open]
    truncated = truncated.rstrip() + "..."
    return close_unclosed_tags(truncated)

class TelegramPublisher:
    def __init__(self, bot_token: str, channel_chat_id: str, admin_chat_id: str = ""):
        self.bot_token = bot_token
        self.channel_chat_id = channel_chat_id
        self.admin_chat_id = admin_chat_id
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.http_session = requests.Session()
        self.http_session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        })

    def send_to_channel(self, title: str, post_text: str, has_media: bool = False, media_urls: List[str] = None) -> Tuple[bool, str]:
        """Publishes post directly to Telegram channel (single photo or multi-photo album). Returns (success, error_message)."""
        if not self.bot_token or not self.channel_chat_id:
            msg = "Telegram bot token or channel chat ID not configured!"
            logger.error(msg)
            return False, msg

        media_urls = media_urls or []
        formatted_text = f"{title}\n\n{post_text}"

        try:
            photos_bytes = []
            if has_media and media_urls:
                for u in media_urls[:4]:
                    b = self._download_image_bytes(u)
                    if b:
                        photos_bytes.append(b)

            # Fallback: if no photos downloaded or item has no native media, generate card
            if not photos_bytes:
                try:
                    from card_generator import CardGenerator
                    from config import Config
                    watermark = getattr(Config, "WATERMARK_TEXT", "@CRETH")
                    card_b = CardGenerator.create_card(
                        title=title,
                        category="CRETH",
                        source_image_bytes=None,
                        watermark_text=watermark
                    )
                    if card_b:
                        photos_bytes.append(card_b)
                except Exception as card_err:
                    logger.warning(f"Fallback card generation failed in send_to_channel: {card_err}")

            if len(photos_bytes) == 1:
                # Single photo sendPhoto
                url = f"{self.api_url}/sendPhoto"
                files = {"photo": ("image.jpg", photos_bytes[0], "image/jpeg")}
                data = {
                    "chat_id": self.channel_chat_id,
                    "caption": safe_html_truncate(formatted_text, 950),
                    "parse_mode": "HTML"
                }
                resp = requests.post(url, data=data, files=files, timeout=15)
                if resp.status_code == 200:
                    return True, ""
                
                # HTML retry fallback with plain text caption
                logger.warning(f"Photo post HTML sendPhoto failed ({resp.text[:100]}), retrying plain text caption...")
                clean_caption = re.sub(r'<[^>]+>', '', formatted_text)[:950]
                data["caption"] = clean_caption
                data.pop("parse_mode", None)
                resp2 = requests.post(url, data=data, files=files, timeout=15)
                if resp2.status_code == 200:
                    return True, ""

            elif len(photos_bytes) > 1:
                # Multi photo sendMediaGroup album
                url = f"{self.api_url}/sendMediaGroup"
                media_attachments = []
                files = {}
                for idx, p_bytes in enumerate(photos_bytes):
                    attach_key = f"photo_{idx}"
                    item = {"type": "photo", "media": f"attach://{attach_key}"}
                    if idx == 0:
                        item["caption"] = safe_html_truncate(formatted_text, 950)
                        item["parse_mode"] = "HTML"
                    media_attachments.append(item)
                    files[attach_key] = (f"photo_{idx}.jpg", p_bytes, "image/jpeg")

                data = {"chat_id": self.channel_chat_id, "media": json.dumps(media_attachments)}
                resp = requests.post(url, data=data, files=files, timeout=20)
                if resp.status_code == 200:
                    return True, ""

                # Retrying album with plain text caption
                logger.warning(f"Media group album HTML failed ({resp.text[:100]}), retrying plain text caption...")
                clean_caption = re.sub(r'<[^>]+>', '', formatted_text)[:950]
                media_attachments[0]["caption"] = clean_caption
                media_attachments[0].pop("parse_mode", None)
                data["media"] = json.dumps(media_attachments)
                resp2 = requests.post(url, data=data, files=files, timeout=20)
                if resp2.status_code == 200:
                    return True, ""

            return self._send_plain_text(self.channel_chat_id, formatted_text)
        except Exception as e:
            err_msg = f"Error publishing to channel: {e}"
            logger.error(err_msg)
            return False, err_msg

    def send_admin_preview(self, db_id: int, title: str, post_text: str, author: str,
                           has_media: bool = False, media_urls: List[str] = None,
                           twitter_post: str = "", sniper_reply: str = "", target_platform: str = "BOTH",
                           ai_opinion: str = "", source_url: str = "") -> bool:
        """Sends clean draft preview to ADMIN_CHAT_ID with high-signal 2-row buttons."""
        if not self.bot_token or not self.admin_chat_id:
            logger.error("Telegram bot token or admin chat ID not configured for ADMIN_PREVIEW mode!")
            return False

        from config import Config
        version_str = getattr(Config, "BOT_VERSION", "v3.2.0")
        header = f"⚡ <b>ПОСТ ДЛЯ МОДЕРАЦИИ #{db_id}</b> [{version_str}] (@{author})\n"
        if source_url:
            header += f"🔗 <b>Источник:</b> <a href='{source_url}'>Перейти к оригиналу</a>\n"
        if ai_opinion:
            header += f"💡 <b>ИИ:</b> {ai_opinion}\n"
        header += "-----------------------------------------\n\n"

        formatted_text = f"{header}📱 <b>TELEGRAM:</b>\n{title}\n\n{post_text}"
        if twitter_post:
            formatted_text += f"\n\n-----------------------------------------\n🐦 <b>X (TWITTER):</b>\n<code>{twitter_post}</code>"

        # Construct Web Intent for Sniper Reply
        tweet_id_match = re.search(r'status/(\d+)', str(source_url))
        tweet_num_id = tweet_id_match.group(1) if tweet_id_match else ""
        
        sniper_intent_url = ""
        if sniper_reply:
            encoded_reply = urllib.parse.quote(sniper_reply, safe='')
            if tweet_num_id:
                sniper_intent_url = f"https://twitter.com/intent/tweet?in_reply_to={tweet_num_id}&text={encoded_reply}"
            else:
                sniper_intent_url = f"https://twitter.com/intent/tweet?text={encoded_reply}"
            formatted_text += f"\n\n-----------------------------------------\n💬 <b>SNIPER REPLY (КОММЕНТАРИЙ В X):</b>\n<code>{sniper_reply}</code>"

        # Check if twitter_thread is available
        twitter_thread = twitter_thread if 'twitter_thread' in locals() else []
        if twitter_thread and len(twitter_thread) > 1:
            formatted_text += f"\n\n-----------------------------------------\n🧵 <b>ТВИТТЕР-ТРЕД ({len(twitter_thread)} ТВИТА):</b>\n"
            for tw in twitter_thread:
                formatted_text += f"<code>{tw}</code>\n\n"

        # Button keyboard layout including Sniper Reply and Thread posting
        keyboard_row_1 = [
            {"text": "📢 В TG канал", "callback_data": f"pub_{db_id}"},
            {"text": "🚀 В X (с картинкой)", "callback_data": f"pubx_{db_id}"}
        ]
        keyboard_row_2 = [
            {"text": "🧵 Тред в X (с картинкой)", "callback_data": f"pubthread_{db_id}"}
        ]
        if sniper_intent_url:
            keyboard_row_2.append({"text": "💬 Sniper Reply", "url": sniper_intent_url})

        keyboard_row_3 = [
            {"text": "🔄 AI Рерайт", "callback_data": f"ai_rewrite_{db_id}"},
            {"text": "❌ Отклонить", "callback_data": f"rej_{db_id}"}
        ]

        inline_keyboard = {
            "inline_keyboard": [
                keyboard_row_1,
                keyboard_row_2,
                keyboard_row_3
            ]
        }

        try:
            photos_bytes = []
            if has_media and media_urls:
                for media_url in media_urls[:4]:
                    b = self._download_image_bytes(media_url)
                    if b:
                        photos_bytes.append(b)

            # Fallback: if no photos downloaded or item has no native media, generate a sleek dark visual card
            if not photos_bytes:
                try:
                    from card_generator import CardGenerator
                    watermark = getattr(Config, "WATERMARK_TEXT", "@CRETH")
                    card_b = CardGenerator.create_card(
                        title=title,
                        category="CRETH",
                        source_image_bytes=None,
                        watermark_text=watermark
                    )
                    if card_b:
                        photos_bytes.append(card_b)
                except Exception as card_err:
                    logger.warning(f"Fallback card generation failed in admin preview: {card_err}")

            if len(photos_bytes) == 1:
                url = f"{self.api_url}/sendPhoto"
                files = {"photo": ("image.jpg", photos_bytes[0], "image/jpeg")}
                data = {
                    "chat_id": self.admin_chat_id,
                    "caption": safe_html_truncate(formatted_text, 950),
                    "parse_mode": "HTML",
                    "reply_markup": json.dumps(inline_keyboard)
                }

                resp = requests.post(url, data=data, files=files, timeout=15)
                if resp.status_code == 200:
                    logger.info(f"Successfully sent photo admin preview #{db_id}")
                    return True
                else:
                    clean_caption = re.sub(r'<[^>]+>', '', formatted_text)[:950]
                    data["caption"] = clean_caption
                    data.pop("parse_mode", None)
                    resp2 = requests.post(url, data=data, files=files, timeout=15)
                    if resp2.status_code == 200:
                        return True

            elif len(photos_bytes) > 1:
                url = f"{self.api_url}/sendMediaGroup"
                media_attachments = []
                files = {}
                for idx, p_bytes in enumerate(photos_bytes):
                    attach_key = f"photo_{idx}"
                    item = {"type": "photo", "media": f"attach://{attach_key}"}
                    if idx == 0:
                        item["caption"] = safe_html_truncate(formatted_text, 950)
                        item["parse_mode"] = "HTML"
                    media_attachments.append(item)
                    files[attach_key] = (f"photo_{idx}.jpg", p_bytes, "image/jpeg")

                data = {"chat_id": self.admin_chat_id, "media": json.dumps(media_attachments)}
                resp = requests.post(url, data=data, files=files, timeout=20)
                album_success = (resp.status_code == 200)

                if album_success:
                    msg_url = f"{self.api_url}/sendMessage"
                    msg_payload = {
                        "chat_id": self.admin_chat_id,
                        "text": f"⚡ <b>Управление публикацией #{db_id} (@{author})</b>",
                        "parse_mode": "HTML",
                        "reply_markup": json.dumps(inline_keyboard)
                    }
                    requests.post(msg_url, json=msg_payload, timeout=10)
                    return True

            url = f"{self.api_url}/sendMessage"
            payload = {
                "chat_id": self.admin_chat_id,
                "text": formatted_text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
                "link_preview_options": {"is_disabled": True},
                "reply_markup": json.dumps(inline_keyboard)
            }
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                return True
            else:
                clean_text = re.sub(r'<[^>]+>', '', formatted_text)
                payload["text"] = clean_text
                payload.pop("parse_mode", None)
                resp2 = requests.post(url, json=payload, timeout=15)
                return resp2.status_code == 200
        except Exception as e:
            logger.error(f"Error sending admin preview: {e}")
            return False

    def _download_image_bytes(self, image_url: str) -> Optional[bytes]:
        """Downloads image bytes with retry mechanism and applies brand watermark overlay."""
        if not image_url:
            return None
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Referer": "https://x.com/"
        }
        for attempt in range(2):
            try:
                r = self.http_session.get(image_url, headers=headers, timeout=12)
                if r.status_code == 200 and len(r.content) > 500:
                    raw_bytes = r.content
                    from config import Config
                    if getattr(Config, "ENABLE_WATERMARK", True):
                        from watermark_processor import apply_watermark
                        watermark_text = getattr(Config, "WATERMARK_TEXT", "@CryptoChannel")
                        return apply_watermark(raw_bytes, watermark_text)
                    return raw_bytes
                else:
                    logger.warning(f"Image download attempt {attempt+1} status {r.status_code} for {image_url}")
            except Exception as e:
                logger.warning(f"Failed image download attempt {attempt+1} for {image_url}: {e}")
            time.sleep(1)
        return None

    def _send_plain_text(self, chat_id: str, text: str) -> Tuple[bool, str]:
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "link_preview_options": {"is_disabled": True}
        }
        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code == 200:
            return True, ""
        
        clean_text = re.sub(r'<[^>]+>', '', text)
        payload["text"] = clean_text
        payload.pop("parse_mode", None)
        resp2 = requests.post(url, json=payload, timeout=15)
        if resp2.status_code == 200:
            return True, ""
        return False, f"Telegram API error: {resp.text}"

    def answer_callback_query(self, callback_query_id: str, text: str = "", show_alert: bool = False):
        try:
            url = f"{self.api_url}/answerCallbackQuery"
            payload = {"callback_query_id": callback_query_id, "text": text, "show_alert": show_alert}
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            logger.error(f"Error answering callback query: {e}")

    def edit_message_text(self, chat_id: int, message_id: int, text: str):
        try:
            url = f"{self.api_url}/editMessageText"
            payload = {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
                "link_preview_options": {"is_disabled": True}
            }
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code != 200:
                clean_text = re.sub(r'<[^>]+>', '', text)
                payload["text"] = clean_text
                payload.pop("parse_mode", None)
                requests.post(url, json=payload, timeout=10)
        except Exception as e:
            logger.error(f"Error editing message text: {e}")

    def _async_process_pub_tg(self, post_id: int, chat_id: int, msg_id: int, db):
        """Asynchronous worker method to publish post to Telegram channel without blocking callback loop."""
        post = db.get_pending_post(post_id)
        if not post:
            return
        success, err_msg = self.send_to_channel(
            post["title"], post["post_text"], post["has_media"], post["media_urls"]
        )
        if success:
            db.update_pending_post_status(post_id, "PUBLISHED")
            new_text = f"✅ <b>[ПОСТ #{post_id} ОПУБЛИКОВАН В КАНАЛ {self.channel_chat_id}]</b>\n\n{post['title']}\n\n{post['post_text']}"
            self.edit_message_text(chat_id, msg_id, new_text)
        else:
            alert_msg = f"❌ <b>Ошибка публикации #{post_id}:</b> {err_msg if err_msg else 'Бот не админ в канале'}"
            logger.warning(alert_msg)
            self._send_plain_text(str(chat_id), alert_msg)

    def _async_process_pub_x(self, post_id: int, chat_id: int, msg_id: int, db):
        """Asynchronous worker method to generate card and post to X via Playwright without blocking callback loop."""
        post = db.get_pending_post(post_id)
        if not post:
            return
        try:
            from card_generator import CardGenerator
            from twitter_poster import TwitterPoster
            from config import Config

            source_bytes = None
            if post.get("media_urls"):
                source_bytes = self._download_image_bytes(post["media_urls"][0])

            watermark = getattr(Config, "WATERMARK_TEXT", "@CRETH")
            card_bytes = CardGenerator.create_card(
                title=post["title"],
                category="CRETH",
                source_image_bytes=source_bytes,
                watermark_text=watermark
            )

            temp_card_path = os.path.join(tempfile.gettempdir(), f"tw_card_{post_id}_{int(time.time())}.jpg")
            with open(temp_card_path, "wb") as f:
                f.write(card_bytes)

            poster = TwitterPoster()
            tweet_text = post.get("twitter_post") or post["title"]
            success, err_msg = poster.post_reply(
                tweet_id="",
                reply_text=tweet_text,
                source_url=post.get("source_url", ""),
                media_urls=[temp_card_path]
            )

            if os.path.exists(temp_card_path):
                try: os.remove(temp_card_path)
                except Exception: pass

            if success:
                updated_msg = f"🚀 <b>[ПОСТ #{post_id} ОПУБЛИКОВАН В X С ИНФОГРАФИКОЙ]</b>\n\n{post['title']}\n\n{post['post_text']}"
                self.edit_message_text(chat_id, msg_id, updated_msg)
            else:
                alert_msg = f"⚠️ <b>Ошибка выгрузки в X #{post_id}:</b> {err_msg}"
                logger.warning(alert_msg)
                self._send_plain_text(str(chat_id), alert_msg)
        except Exception as e:
            logger.error(f"Error publishing card post to X: {e}")
            self._send_plain_text(str(chat_id), f"⚠️ Ошибка генерации/выгрузки карточки в X: {e}")

    def _async_process_pub_thread(self, post_id: int, chat_id: int, msg_id: int, db):
        """Asynchronous worker method to post multi-tweet thread to X via Playwright."""
        post = db.get_pending_post(post_id)
        if not post:
            return
        try:
            from card_generator import CardGenerator
            from twitter_poster import TwitterPoster
            from config import Config

            tweets = post.get("twitter_thread") or []
            if not tweets or len(tweets) < 2:
                # Fallback: create structured 3-tweet thread from post content
                tweets = [
                    f"1/3 🚨 BREAKING: {post['title']} $CRETH ⚡",
                    f"2/3 📊 On-Chain Breakdown:\n{re.sub(r'<[^>]+>', '', post['post_text'])[:200]}...",
                    "3/3 🧵 Follow @CRETH for real-time Web3 & on-chain alerts 🎯"
                ]

            source_bytes = None
            if post.get("media_urls"):
                source_bytes = self._download_image_bytes(post["media_urls"][0])

            watermark = getattr(Config, "WATERMARK_TEXT", "@CRETH")
            card_bytes = CardGenerator.create_card(
                title=post["title"],
                category="CRETH",
                source_image_bytes=source_bytes,
                watermark_text=watermark
            )

            temp_card_path = os.path.join(tempfile.gettempdir(), f"tw_thread_card_{post_id}_{int(time.time())}.jpg")
            with open(temp_card_path, "wb") as f:
                f.write(card_bytes)

            poster = TwitterPoster()
            success, err_msg = poster.post_thread(
                tweets=tweets,
                media_urls=[temp_card_path]
            )

            if os.path.exists(temp_card_path):
                try: os.remove(temp_card_path)
                except Exception: pass

            if success:
                updated_msg = f"🧵 <b>[ТВИТТЕР-ТРЕД ИЗ {len(tweets)} ТВИТОВ ОПУБЛИКОВАН В X С ОБЛОЖКОЙ]</b>\n\n{post['title']}\n\n{post['post_text']}"
                self.edit_message_text(chat_id, msg_id, updated_msg)
            else:
                alert_msg = f"⚠️ <b>Ошибка выгрузки треда в X #{post_id}:</b> {err_msg}"
                logger.warning(alert_msg)
                self._send_plain_text(str(chat_id), alert_msg)
        except Exception as e:
            logger.error(f"Error publishing thread to X: {e}")
            self._send_plain_text(str(chat_id), f"⚠️ Ошибка генерации/выгрузки треда в X: {e}")

    def _async_process_ai_rewrite(self, post_id: int, chat_id: int, msg_id: int, db, ai_editor):
        """Asynchronous worker method to re-edit post using OpenRouter AI without blocking callback loop."""
        post = db.get_pending_post(post_id)
        if not post:
            return
        try:
            new_title, new_text = ai_editor.reedit_post(post["title"], post["post_text"], "REWRITE")
            db.update_pending_post_text(post_id, new_title, new_text)
            updated_full_text = f"✨ <b>[ПОСТ #{post_id} ПЕРЕРАБОТАН ИИ]</b>\n\n{new_title}\n\n{new_text}"
            self.edit_message_text(chat_id, msg_id, updated_full_text)
        except Exception as e:
            logger.error(f"Error in AI rewrite worker: {e}")
            self._send_plain_text(str(chat_id), f"⚠️ Ошибка переработки ИИ: {e}")

    def start_callback_listener(self, db):
        """Starts a background thread to poll Telegram for inline button clicks."""
        thread = threading.Thread(target=self._poll_callbacks_loop, args=(db,), daemon=True)
        thread.start()
        logger.info("Telegram callback listener thread started successfully.")

    def _poll_callbacks_loop(self, db):
        from ai_editor import AIEditor
        from config import Config

        ai_editor = AIEditor(
            openrouter_key=Config.OPENROUTER_API_KEY,
            model_name=Config.OPENROUTER_MODEL,
            base_url=Config.OPENROUTER_BASE_URL
        )

        offset = 0
        while True:
            try:
                url = f"{self.api_url}/getUpdates"
                payload = {"offset": offset, "timeout": 20, "allowed_updates": ["callback_query", "message"]}
                resp = requests.post(url, json=payload, timeout=25)
                if resp.status_code == 200:
                    data = resp.json()
                    for update in data.get("result", []):
                        offset = update["update_id"] + 1

                        # Handle Admin Text Commands (e.g., /stats)
                        msg_obj = update.get("message")
                        if msg_obj and msg_obj.get("text"):
                            cmd_text = msg_obj.get("text", "").strip()
                            sender_id = str(msg_obj.get("from", {}).get("id"))
                            if cmd_text in ["/stats", "/stats@CryptoBot"]:
                                if not self.admin_chat_id or sender_id == str(self.admin_chat_id):
                                    stats = db.get_analytics_summary()
                                    stats_msg = (
                                        "<b>📊 АНАЛИТИКА И ЮНИТ-ЭКОНОМИКА БОТА</b>\n"
                                        "-----------------------------------------\n"
                                        f"📦 Всего новостей обработано: <b>{stats['total_items']}</b>\n"
                                        f"📢 Опубликовано в канал: <b>{stats['published_items']}</b>\n"
                                        f"👁 Суммарные просмотры: <b>{stats['total_views']}</b>\n"
                                        f"💸 Расход LLM API (OpenRouter): <b>${stats['total_cost_usd']}</b>\n"
                                        f"💎 Себестоимость 1 поста: <b>${stats['avg_cost_per_post_usd']}</b>\n"
                                    )
                                    self._send_plain_text(sender_id, stats_msg)
                                continue

                        cb = update.get("callback_query")
                        if not cb:
                            continue

                        cb_id = cb.get("id")
                        cb_data = cb.get("data", "")
                        from_user = str(cb.get("from", {}).get("id"))
                        msg = cb.get("message", {})
                        msg_id = msg.get("message_id")
                        chat_id = msg.get("chat", {}).get("id")

                        if self.admin_chat_id and from_user != str(self.admin_chat_id):
                            self.answer_callback_query(cb_id, "⚠️ Access Denied", show_alert=True)
                            continue

                        if cb_data.startswith("pub_"):
                            post_id = int(cb_data.split("pub_")[1])
                            self.answer_callback_query(cb_id, "⏳ Публикуем в Telegram...")
                            threading.Thread(
                                target=self._async_process_pub_tg,
                                args=(post_id, chat_id, msg_id, db),
                                daemon=True
                            ).start()

                        elif cb_data.startswith("pubx_"):
                            post_id = int(cb_data.split("pubx_")[1])
                            self.answer_callback_query(cb_id, "⏳ Генерируем карточку и выгружаем в X...")
                            threading.Thread(
                                target=self._async_process_pub_x,
                                args=(post_id, chat_id, msg_id, db),
                                daemon=True
                            ).start()

                        elif cb_data.startswith("pubthread_"):
                            post_id = int(cb_data.split("pubthread_")[1])
                            self.answer_callback_query(cb_id, "⏳ Генерируем тред и выгружаем в X...")
                            threading.Thread(
                                target=self._async_process_pub_thread,
                                args=(post_id, chat_id, msg_id, db),
                                daemon=True
                            ).start()

                        elif cb_data.startswith("rej_"):
                            post_id = int(cb_data.split("rej_")[1])
                            post = db.get_pending_post(post_id)
                            if post:
                                db.update_pending_post_status(post_id, "REJECTED")
                                self.answer_callback_query(cb_id, "❌ Пост отклонен")
                                new_text = f"❌ <b>[ПОСТ #{post_id} ОТКЛОНЕН]</b>\n\n{post['title']}\n\n{post['post_text']}"
                                self.edit_message_text(chat_id, msg_id, new_text)
                            else:
                                self.answer_callback_query(cb_id, "❌ Пост не найден", show_alert=True)

                        elif cb_data.startswith("ai_"):
                            post_id = int(cb_data.split("_")[-1])
                            self.answer_callback_query(cb_id, "⏳ ИИ перерабатывает пост...")
                            threading.Thread(
                                target=self._async_process_ai_rewrite,
                                args=(post_id, chat_id, msg_id, db, ai_editor),
                                daemon=True
                            ).start()

            except Exception as e:
                logger.error(f"Error in Telegram callback listener loop: {e}")
                time.sleep(3)
