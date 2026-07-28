import logging
import asyncio
import re
import urllib.parse
import requests
from config import Config

logger = logging.getLogger("TwitterPoster")

class TwitterPoster:
    def __init__(self, auth_token: str = None, ct0: str = None, twid: str = None):
        self.auth_token = auth_token or Config.TWITTER_AUTH_TOKEN
        self.ct0 = ct0 or Config.TWITTER_CT0
        self.twid = twid or Config.TWITTER_TWID

    def post_reply(self, tweet_id: str, reply_text: str, source_url: str = "") -> tuple[bool, str]:
        """
        Posts a reply comment or new tweet to Twitter (X) using Playwright.
        Returns (success: bool, error_message: str).
        """
        if not self.auth_token or not self.ct0:
            err = "Twitter cookies (TWITTER_AUTH_TOKEN and TWITTER_CT0) are missing in .env!"
            logger.error(err)
            return False, err

        # Extract numeric tweet ID if present in tweet_id or source_url
        numeric_id_match = re.search(r'status/(\d+)', str(source_url)) or re.search(r'(\d{15,25})', str(tweet_id))
        
        if numeric_id_match:
            real_tweet_id = numeric_id_match.group(1)
            target_url = f"https://x.com/i/status/{real_tweet_id}"
            is_reply = True
        else:
            # If it's a news article (non-tweet), compose a tweet intent
            encoded_text = urllib.parse.quote(reply_text)
            target_url = f"https://x.com/intent/tweet?text={encoded_text}"
            is_reply = False

        try:
            logger.info(f"Posting to Twitter via Playwright ({target_url})...")
            import sys
            import asyncio
            
            if sys.platform == "win32":
                loop = asyncio.ProactorEventLoop()
            else:
                loop = asyncio.new_event_loop()
                
            asyncio.set_event_loop(loop)
            try:
                res = loop.run_until_complete(self._playwright_post(target_url, reply_text, is_reply))
                return res
            finally:
                loop.close()
        except Exception as e:
            logger.warning(f"Playwright error: {e}")
            return False, f"Playwright error: {e}"

    async def _playwright_post(self, target_url: str, reply_text: str, is_reply: bool) -> tuple[bool, str]:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 900}
            )

            # Inject cookies
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
                # Find reply textarea
                reply_box = await page.wait_for_selector('div[data-testid="tweetTextarea_0"], div[contenteditable="true"]', timeout=10000)
                if not reply_box:
                    await browser.close()
                    return False, "Could not locate reply box on Twitter page"

                await reply_box.click()
                await reply_box.fill(reply_text)
                await page.wait_for_timeout(1000)

                reply_button = await page.wait_for_selector('button[data-testid="tweetButtonInline"], button[data-testid="tweetButton"]', timeout=5000)
                if not reply_button:
                    await browser.close()
                    return False, "Could not locate Reply submit button"

                await reply_button.click()
                await page.wait_for_timeout(3000)
            else:
                # Intent tweet / new tweet posting
                submit_button = await page.wait_for_selector('button[data-testid="tweetButton"], button[data-testid="tweetButtonInline"]', timeout=10000)
                if not submit_button:
                    await browser.close()
                    return False, "Could not locate Post button on Twitter intent page"

                await submit_button.click()
                await page.wait_for_timeout(3000)

            await browser.close()
            logger.info(f"Successfully posted to Twitter via Playwright ({target_url})!")
            return True, ""
