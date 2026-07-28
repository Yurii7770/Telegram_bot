import logging
import requests
import json
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("TelegramPublisher")

class TelegramPublisher:
    def __init__(self, bot_token: str, channel_chat_id: str, admin_chat_id: str = ""):
        self.bot_token = bot_token
        self.channel_chat_id = channel_chat_id
        self.admin_chat_id = admin_chat_id
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_to_channel(self, title: str, post_text: str, has_media: bool = False, media_urls: List[str] = None) -> Tuple[bool, str]:
        """Publishes post directly to Telegram channel. Returns (success, error_message)."""
        if not self.bot_token or not self.channel_chat_id:
            msg = "Telegram bot token or channel chat ID not configured!"
            logger.error(msg)
            return False, msg

        media_urls = media_urls or []
        formatted_text = f"{title}\n\n{post_text}"

        try:
            if has_media and media_urls:
                photo_url = media_urls[0]
                url = f"{self.api_url}/sendPhoto"
                payload = {
                    "chat_id": self.channel_chat_id,
                    "photo": photo_url,
                    "caption": formatted_text,
                    "parse_mode": "HTML"
                }
                resp = requests.post(url, json=payload, timeout=15)
                if resp.status_code == 200:
                    return True, ""
                
                logger.warning(f"Photo post failed ({resp.text[:100]}), falling back to sendMessage")
                return self._send_plain_text(self.channel_chat_id, formatted_text)
            else:
                return self._send_plain_text(self.channel_chat_id, formatted_text)
        except Exception as e:
            err_msg = f"Error publishing to channel: {e}"
            logger.error(err_msg)
            return False, err_msg

    def send_admin_preview(self, db_id: int, title: str, post_text: str, author: str,
                           has_media: bool = False, media_urls: List[str] = None,
                           sniper_reply: str = "", target_platform: str = "BOTH",
                           ai_opinion: str = "", source_url: str = "") -> bool:
        """Sends post draft to ADMIN_CHAT_ID with explicit source link, AI opinion, and buttons."""
        if not self.bot_token or not self.admin_chat_id:
            logger.error("Telegram bot token or admin chat ID not configured for ADMIN_PREVIEW mode!")
            return False

        media_urls = media_urls or []
        header = f"⚡ <b>[СВЕЖЕЕ ОПОВЕЩЕНИЕ #{db_id}]</b>\n"
        header += f"👤 <b>Автор:</b> @{author}\n"
        if source_url:
            header += f"🔗 <b>Ссылка на пост:</b> <a href='{source_url}'>{source_url}</a>\n"
        header += "\n"
        
        if ai_opinion or target_platform:
            header += f"🤖 <b>МНЕНИЕ И РЕКОМЕНДАЦИЯ ИИ:</b>\n{ai_opinion or 'Рекомендуется к просмотру'}\n"
            header += f"🎯 <b>Целевая платформа:</b> <code>{target_platform}</code>\n"
            header += "-----------------------------------------\n\n"

        formatted_text = f"{header}📱 <b>ПОСТ ДЛЯ TELEGRAM КАНАЛА:</b>\n{title}\n\n{post_text}"

        if sniper_reply:
            formatted_text += f"\n\n-----------------------------------------\n🐦 <b>SNIPER REPLY ДЛЯ TWITTER (Кликните для копирования):</b>\n<code>{sniper_reply}</code>"

        inline_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ В Telegram канал", "callback_data": f"pub_{db_id}"},
                    {"text": "🐦 В Twitter (Sniper)", "callback_data": f"xreply_{db_id}"}
                ],
                [
                    {"text": "❌ Отклонить", "callback_data": f"rej_{db_id}"}
                ]
            ]
        }

        try:
            if has_media and media_urls:
                photo_url = media_urls[0]
                url = f"{self.api_url}/sendPhoto"
                
                photo_caption = formatted_text
                if len(photo_caption) > 1000:
                    clean_caption = re.sub(r'<[^>]+>', '', photo_caption[:990]) + "..."
                    payload = {
                        "chat_id": self.admin_chat_id,
                        "photo": photo_url,
                        "caption": clean_caption,
                        "reply_markup": json.dumps(inline_keyboard)
                    }
                else:
                    payload = {
                        "chat_id": self.admin_chat_id,
                        "photo": photo_url,
                        "caption": photo_caption,
                        "parse_mode": "HTML",
                        "reply_markup": json.dumps(inline_keyboard)
                    }

                resp = requests.post(url, json=payload, timeout=15)
                if resp.status_code == 200:
                    logger.info(f"Successfully sent photo admin preview #{db_id} to admin {self.admin_chat_id}")
                    return True
                else:
                    logger.warning(f"Photo admin preview failed ({resp.text[:100]}), retrying with clean photo caption fallback...")
                    clean_caption = re.sub(r'<[^>]+>', '', formatted_text[:990]) + "..."
                    payload["caption"] = clean_caption
                    payload.pop("parse_mode", None)
                    resp2 = requests.post(url, json=payload, timeout=15)
                    if resp2.status_code == 200:
                        logger.info(f"Successfully sent photo admin preview #{db_id} with clean caption fallback")
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
                logger.info(f"Successfully sent admin preview #{db_id} to admin {self.admin_chat_id}")
                return True
            else:
                logger.warning(f"Telegram admin preview HTML error ({resp.text[:100]}), attempting clean text fallback...")
                clean_text = re.sub(r'<[^>]+>', '', formatted_text)
                payload["text"] = clean_text
                payload.pop("parse_mode", None)
                resp2 = requests.post(url, json=payload, timeout=15)
                if resp2.status_code == 200:
                    logger.info(f"Successfully sent admin preview #{db_id} to admin using clean text fallback")
                    return True
                else:
                    logger.error(f"Failed to send admin preview even with plain text: {resp2.text}")
                    return False
        except Exception as e:
            logger.error(f"Error sending admin preview: {e}")
            return False

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
            logger.info("Successfully sent message to Telegram.")
            return True, ""
        
        # If HTML parsing failed, try stripping HTML tags as final fallback
        logger.warning(f"Telegram sendMessage error code {resp.status_code} ({resp.text[:100]}), trying clean text fallback...")
        clean_text = re.sub(r'<[^>]+>', '', text)
        payload["text"] = clean_text
        payload.pop("parse_mode", None)
        resp2 = requests.post(url, json=payload, timeout=15)
        if resp2.status_code == 200:
            return True, ""
        else:
            err_details = resp.text
            if "Forbidden: bot is not a member" in err_details or "chat not found" in err_details:
                return False, f"Бот не добавлен в администраторы канала {self.channel_chat_id}!"
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

    def start_callback_listener(self, db):
        """Starts a background thread to poll Telegram for inline button clicks."""
        import threading
        thread = threading.Thread(target=self._poll_callbacks_loop, args=(db,), daemon=True)
        thread.start()
        logger.info("Telegram callback listener thread started successfully.")

    def _poll_callbacks_loop(self, db):
        import time
        offset = 0
        while True:
            try:
                url = f"{self.api_url}/getUpdates"
                payload = {"offset": offset, "timeout": 20, "allowed_updates": ["callback_query"]}
                resp = requests.post(url, json=payload, timeout=25)
                if resp.status_code == 200:
                    data = resp.json()
                    for update in data.get("result", []):
                        offset = update["update_id"] + 1
                        cb = update.get("callback_query")
                        if not cb:
                            continue

                        cb_id = cb.get("id")
                        cb_data = cb.get("data", "")
                        from_user = str(cb.get("from", {}).get("id"))
                        msg = cb.get("message", {})
                        msg_id = msg.get("message_id")
                        chat_id = msg.get("chat", {}).get("id")

                        # Verify admin authorization
                        if self.admin_chat_id and from_user != str(self.admin_chat_id):
                            self.answer_callback_query(cb_id, "⚠️ Access Denied", show_alert=True)
                            continue

                        if cb_data.startswith("pub_"):
                            post_id = int(cb_data.split("pub_")[1])
                            post = db.get_pending_post(post_id)
                            if post:
                                success, err_msg = self.send_to_channel(
                                    post["title"], post["post_text"], post["has_media"], post["media_urls"]
                                )

                                if success:
                                    db.update_pending_post_status(post_id, "PUBLISHED")
                                    self.answer_callback_query(cb_id, "✅ Пост опубликован в канал!")
                                    new_text = f"✅ <b>[ПОСТ #{post_id} ОПУБЛИКОВАН В КАНАЛ {self.channel_chat_id}]</b>\n\n{post['title']}\n\n{post['post_text']}"
                                    self.edit_message_text(chat_id, msg_id, new_text)
                                else:
                                    # Show explicit alert on failure (e.g. Bot not admin)
                                    alert_msg = f"❌ Ошибка публикации: {err_msg if err_msg else 'Бот не админ в канале'}"
                                    logger.warning(f"Publish failed for post #{post_id}: {alert_msg}")
                                    self.answer_callback_query(cb_id, alert_msg, show_alert=True)
                            else:
                                self.answer_callback_query(cb_id, "❌ Пост не найден", show_alert=True)

                        elif cb_data.startswith("xreply_"):
                            post_id = int(cb_data.split("xreply_")[1])
                            post = db.get_pending_post(post_id)
                            if post and post.get("sniper_reply"):
                                from twitter_poster import TwitterPoster
                                poster = TwitterPoster()
                                source_link = post.get("source_url") or post.get("tweet_id", "")
                                success, err_msg = poster.post_reply(post["tweet_id"], post["sniper_reply"], source_link)
                                if success:
                                    self.answer_callback_query(cb_id, "🚀 Ответ успешно опубликован в Twitter!", show_alert=True)
                                    new_text = f"🐦 <b>[ОТВЕТ ОПУБЛИКОВАН В TWITTER ПОД ТВИТОМ @{post['author']}]</b>\n\n💬 <code>{post['sniper_reply']}</code>"
                                    self.edit_message_text(chat_id, msg_id, new_text)
                                else:
                                    alert_msg = f"⚠️ {err_msg}"
                                    logger.warning(f"Twitter reply failed for post #{post_id}: {alert_msg}")
                                    self.answer_callback_query(cb_id, alert_msg, show_alert=True)
                            else:
                                self.answer_callback_query(cb_id, "❌ Пост или Sniper Reply не найден", show_alert=True)

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
            except Exception as e:
                logger.error(f"Error in Telegram callback listener loop: {e}")
                time.sleep(3)
