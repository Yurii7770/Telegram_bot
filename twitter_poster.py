import logging
import asyncio
import re
import os
import time
import tempfile
import urllib.parse
import requests
from typing import List, Optional, Tuple
from config import Config

logger = logging.getLogger("TwitterPoster")

class TwitterPoster:
    def __init__(self, auth_token: str = None, ct0: str = None, twid: str = None):
        self.auth_token = auth_token or Config.TWITTER_AUTH_TOKEN
        self.ct0 = ct0 or Config.TWITTER_CT0
        self.twid = twid or Config.TWITTER_TWID
        self.http_session = requests.Session()
        self.http_session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        })

    def post_reply(self, tweet_id: str, reply_text: str, source_url: str = "", media_urls: List[str] = None, is_reply: bool = False) -> Tuple[bool, str]:
        """
        Posts a standalone tweet or a reply comment to Twitter (X) using Playwright, including attached images.
        Returns (success: bool, error_message: str).
        """
        if not self.auth_token or not self.ct0:
            err = "Twitter cookies (TWITTER_AUTH_TOKEN and TWITTER_CT0) are missing in .env!"
            logger.error(err)
            return False, err

        numeric_id_match = re.search(r'status/(\d+)', str(source_url)) or re.search(r'(\d{15,25})', str(tweet_id))
        
        if is_reply and numeric_id_match:
            real_tweet_id = numeric_id_match.group(1)
            target_url = f"https://x.com/i/status/{real_tweet_id}"
            is_reply_action = True
        else:
            encoded_text = urllib.parse.quote(reply_text)
            target_url = f"https://twitter.com/intent/tweet?text={encoded_text}"
            is_reply_action = False

        # Download or use local image files if media_urls exist
        local_media_files = []
        temp_files_created = []
        if media_urls:
            for idx, m_url in enumerate(media_urls[:4]):
                if isinstance(m_url, str) and os.path.exists(m_url):
                    local_media_files.append(m_url)
                    continue
                try:
                    r = self.http_session.get(m_url, timeout=10)
                    if r.status_code == 200 and len(r.content) > 500:
                        tf = os.path.join(tempfile.gettempdir(), f"tw_post_img_{idx}_{int(time.time())}.jpg")
                        with open(tf, "wb") as f:
                            f.write(r.content)
                        local_media_files.append(tf)
                        temp_files_created.append(tf)
                except Exception as e:
                    logger.warning(f"Failed to download image for Twitter post ({m_url}): {e}")

        try:
            logger.info(f"Posting to Twitter via Playwright ({target_url}) with {len(local_media_files)} attached images...")
            import sys
            import asyncio
            
            if sys.platform == "win32":
                loop = asyncio.ProactorEventLoop()
            else:
                loop = asyncio.new_event_loop()
                
            asyncio.set_event_loop(loop)
            try:
                res = loop.run_until_complete(self._playwright_post(target_url, reply_text, is_reply_action, local_media_files))
                return res
            finally:
                loop.close()
                for tf in local_media_files:
                    if os.path.exists(tf):
                        try: os.remove(tf)
                        except Exception: pass
        except Exception as e:
            logger.warning(f"Playwright error: {e}")
            for tf in local_media_files:
                if os.path.exists(tf):
                    try: os.remove(tf)
                    except Exception: pass
            return False, f"Playwright error: {e}"

    async def _playwright_post(self, target_url: str, reply_text: str, is_reply: bool, local_media_files: List[str] = None) -> Tuple[bool, str]:
        from playwright.async_api import async_playwright
        local_media_files = local_media_files or []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-software-rasterizer",
                    "--disable-extensions",
                    "--js-flags=--max-old-space-size=128",
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 900}
            )

            cookies = [
                {"name": "auth_token", "value": self.auth_token, "domain": ".x.com", "path": "/"},
                {"name": "ct0", "value": self.ct0, "domain": ".x.com", "path": "/"}
            ]
            if self.twid:
                cookies.append({"name": "twid", "value": self.twid, "domain": ".x.com", "path": "/"})

            await context.add_cookies(cookies)
            page = await context.new_page()

            logger.info(f"Navigating to {target_url}...")
            await page.goto(target_url, timeout=30000)
            await page.wait_for_timeout(3000)

            if is_reply:
                reply_box = await page.wait_for_selector('div[data-testid="tweetTextarea_0"], div[contenteditable="true"]', timeout=10000)
                if not reply_box:
                    await browser.close()
                    return False, "Could not locate reply box on Twitter page"

                await reply_box.click()
                await reply_box.fill(reply_text)
                await page.wait_for_timeout(1000)

                # Attach images if available
                if local_media_files:
                    file_input = await page.query_selector('input[data-testid="fileInput"]')
                    if file_input:
                        logger.info(f"Uploading {len(local_media_files)} image(s) to Twitter reply composer...")
                        await file_input.set_input_files(local_media_files)
                        await page.wait_for_timeout(3000)

                reply_button = await page.wait_for_selector('button[data-testid="tweetButtonInline"], button[data-testid="tweetButton"]', timeout=5000)
                if not reply_button:
                    await browser.close()
                    return False, "Could not locate Reply submit button"

                await reply_button.click()
                await page.wait_for_timeout(4000)
            else:
                # Intent tweet / new tweet posting
                if local_media_files:
                    file_input = await page.query_selector('input[data-testid="fileInput"]')
                    if file_input:
                        logger.info(f"Uploading {len(local_media_files)} image(s) to Twitter intent composer...")
                        await file_input.set_input_files(local_media_files)
                        await page.wait_for_timeout(3000)

                submit_button = await page.wait_for_selector('button[data-testid="tweetButton"], button[data-testid="tweetButtonInline"]', timeout=10000)
                if not submit_button:
                    await browser.close()
                    return False, "Could not locate Post button on Twitter intent page"

                await submit_button.click()
                await page.wait_for_timeout(4000)

            await browser.close()
            logger.info(f"Successfully posted to Twitter with {len(local_media_files)} image(s) via Playwright ({target_url})!")
            return True, ""

    def post_thread(self, tweets: List[str], media_urls: List[str] = None) -> Tuple[bool, str]:
        """
        Posts a multi-tweet thread to Twitter (X) sequentially using Playwright.
        Tweet #1 has attached card image(s). Subsequent tweets are posted sequentially in the thread.
        """
        if not tweets:
            return False, "Empty thread list"
        if not self.auth_token or not self.ct0:
            err = "Twitter cookies (TWITTER_AUTH_TOKEN and TWITTER_CT0) are missing in .env!"
            logger.error(err)
            return False, err

        local_media_files = []
        temp_files_created = []
        if media_urls:
            for idx, m_url in enumerate(media_urls[:4]):
                if isinstance(m_url, str) and os.path.exists(m_url):
                    local_media_files.append(m_url)
                    continue
                try:
                    r = self.http_session.get(m_url, timeout=10)
                    if r.status_code == 200 and len(r.content) > 500:
                        tf = os.path.join(tempfile.gettempdir(), f"tw_thread_img_{idx}_{int(time.time())}.jpg")
                        with open(tf, "wb") as f:
                            f.write(r.content)
                        local_media_files.append(tf)
                        temp_files_created.append(tf)
                except Exception as e:
                    logger.warning(f"Failed to download image for Twitter thread ({m_url}): {e}")

        try:
            logger.info(f"Posting {len(tweets)}-tweet thread to Twitter via Playwright...")
            import sys
            import asyncio

            if sys.platform == "win32":
                loop = asyncio.ProactorEventLoop()
            else:
                loop = asyncio.new_event_loop()

            asyncio.set_event_loop(loop)
            try:
                res = loop.run_until_complete(self._playwright_post_thread(tweets, local_media_files))
                return res
            finally:
                loop.close()
                for tf in temp_files_created:
                    if os.path.exists(tf):
                        try: os.remove(tf)
                        except Exception: pass
        except Exception as e:
            logger.warning(f"Playwright thread error: {e}")
            for tf in temp_files_created:
                if os.path.exists(tf):
                    try: os.remove(tf)
                    except Exception: pass
            return False, f"Playwright thread error: {e}"

    async def _playwright_post_thread(self, tweets: List[str], local_media_files: List[str] = None) -> Tuple[bool, str]:
        from playwright.async_api import async_playwright
        local_media_files = local_media_files or []

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-software-rasterizer",
                    "--disable-extensions",
                    "--js-flags=--max-old-space-size=128",
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 900}
            )

            cookies = [
                {"name": "auth_token", "value": self.auth_token, "domain": ".x.com", "path": "/"},
                {"name": "ct0", "value": self.ct0, "domain": ".x.com", "path": "/"}
            ]
            if self.twid:
                cookies.append({"name": "twid", "value": self.twid, "domain": ".x.com", "path": "/"})

            await context.add_cookies(cookies)
            page = await context.new_page()

            # Step 1: Post Tweet #1 via Intent composer with attached card
            first_tweet_text = tweets[0]
            encoded_first = urllib.parse.quote(first_tweet_text)
            target_url = f"https://twitter.com/intent/tweet?text={encoded_first}"

            logger.info(f"Posting Tweet #1/thread: '{first_tweet_text[:40]}...'")
            await page.goto(target_url, timeout=30000)
            await page.wait_for_timeout(3000)

            if local_media_files:
                file_input = await page.query_selector('input[data-testid="fileInput"]')
                if file_input:
                    logger.info(f"Uploading {len(local_media_files)} image(s) to Tweet #1...")
                    await file_input.set_input_files(local_media_files)
                    await page.wait_for_timeout(3000)

            submit_button = await page.wait_for_selector('button[data-testid="tweetButton"], button[data-testid="tweetButtonInline"]', timeout=10000)
            if not submit_button:
                await browser.close()
                return False, "Could not locate Post button for Tweet #1"

            await submit_button.click()
            await page.wait_for_timeout(4000)

            # Step 2: Post remaining tweets (2..N) sequentially
            for idx, tweet_text in enumerate(tweets[1:], start=2):
                logger.info(f"Posting Tweet #{idx}/{len(tweets)}: '{tweet_text[:40]}...'")
                encoded = urllib.parse.quote(tweet_text)
                target_url = f"https://twitter.com/intent/tweet?text={encoded}"
                await page.goto(target_url, timeout=25000)
                await page.wait_for_timeout(2500)

                sub_btn = await page.wait_for_selector('button[data-testid="tweetButton"], button[data-testid="tweetButtonInline"]', timeout=10000)
                if sub_btn:
                    await sub_btn.click()
                    await page.wait_for_timeout(3500)

            await browser.close()
            logger.info(f"Successfully posted {len(tweets)}-tweet thread to Twitter via Playwright!")
            return True, ""
