import logging
import requests
import bs4
import hashlib
import urllib.parse
import sys
import asyncio
from typing import List, Dict, Optional
from config import Config

logger = logging.getLogger("ContentFetcher")

class ContentFetcher:
    def __init__(self, auth_token: str = "", ct0: str = ""):
        self.auth_token = auth_token or Config.TWITTER_AUTH_TOKEN
        self.ct0 = ct0 or Config.TWITTER_CT0
        self.twid = Config.TWITTER_TWID
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        })

    def fetch_all_sources(self, twitter_accounts: List[str], rss_feeds: List[tuple] = None, enable_rss: bool = False) -> List[Dict]:
        """
        Fetches posts STRICTLY and 100% ONLY from Twitter (X) target accounts.
        """
        all_items = []

        # Fetch Target Twitter accounts strictly
        for username in twitter_accounts:
            tweets = self.get_twitter_posts(username, limit=5)
            all_items.extend(tweets)

        # Generic RSS feeds are completely disabled for Twitter-only mode
        logger.info(f"Total content items fetched across target sources: {len(all_items)}")
        return all_items

    def get_twitter_posts(self, username: str, limit: int = 5) -> List[Dict]:
        """
        Fetches 100% REAL tweets directly from Twitter for a target handle using:
        1. Playwright Direct Timeline Extractor (100% direct x.com/status links & images)
        2. FxTwitter / VxTwitter Profile API fallback
        """
        results = []

        # Method 1: Playwright Direct Twitter Extractor
        try:
            results = self._fetch_via_playwright(username, limit)
            if results:
                logger.info(f"Fetched {len(results)} 100% real tweets for @{username} via Playwright")
                return results
        except Exception as e:
            logger.warning(f"Playwright tweet fetch failed for @{username}: {e}")

        # Method 2: FxTwitter / VxTwitter Profile API fallback
        try:
            url = f"https://api.fxtwitter.com/{username}"
            resp = self.session.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                user_info = data.get("user", {})
                pinned = user_info.get("pinned_tweet")
                if pinned:
                    tweet_id = str(pinned.get("id") or pinned.get("tweetID", ""))
                    text = pinned.get("text", "")
                    if tweet_id and text:
                        results.append({
                            "id": f"tw_{tweet_id}",
                            "author": username,
                            "title": f"Tweet by @{username}",
                            "text": text,
                            "url": f"https://x.com/{username}/status/{tweet_id}",
                            "source_type": "twitter",
                            "has_media": False,
                            "media_urls": []
                        })
                        logger.info(f"Fetched pinned tweet for @{username} via FxTwitter API")
                        return results
        except Exception as e:
            logger.warning(f"FxTwitter fetch failed for @{username}: {e}")

        return results

    def _fetch_via_playwright(self, username: str, limit: int = 5) -> List[Dict]:
        """Uses Playwright to fetch real tweets directly from Twitter profile timeline."""
        if sys.platform == "win32":
            loop = asyncio.ProactorEventLoop()
        else:
            loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._async_playwright_fetch(username, limit))
        finally:
            loop.close()

    async def _async_playwright_fetch(self, username: str, limit: int = 5) -> List[Dict]:
        from playwright.async_api import async_playwright

        results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 900}
            )

            # Inject cookies if present
            if self.auth_token and self.ct0:
                cookies = [
                    {"name": "auth_token", "value": self.auth_token, "domain": ".x.com", "path": "/", "secure": True, "sameSite": "Lax"},
                    {"name": "ct0", "value": self.ct0, "domain": ".x.com", "path": "/", "secure": True, "sameSite": "Lax"}
                ]
                if self.twid:
                    cookies.append({"name": "twid", "value": self.twid, "domain": ".x.com", "path": "/", "secure": True, "sameSite": "Lax"})
                await context.add_cookies(cookies)

            page = await context.new_page()
            target_url = f"https://x.com/{username}"
            await page.goto(target_url, timeout=25000)
            await page.wait_for_timeout(3500)

            tweet_elements = await page.query_selector_all('article[data-testid="tweet"]')
            for el in tweet_elements[:limit]:
                # Extract status link
                link_el = await el.query_selector('a[href*="/status/"]')
                link = await link_el.get_attribute("href") if link_el else ""
                if link and not link.startswith("http"):
                    link = f"https://x.com{link}"

                # Extract tweet text
                text_el = await el.query_selector('div[data-testid="tweetText"]')
                text = await text_el.inner_text() if text_el else ""

                # Extract media images if present
                img_els = await el.query_selector_all('div[data-testid="tweetPhoto"] img')
                media_urls = []
                for img in img_els:
                    src = await img.get_attribute("src")
                    if src and "media" in src:
                        media_urls.append(src)

                if link and text:
                    tweet_id = link.split("/status/")[-1].split("?")[0]

                    # Extract timestamp and filter out old tweets (max 4 hours old)
                    time_el = await el.query_selector('time')
                    datetime_str = await time_el.get_attribute('datetime') if time_el else ""
                    if datetime_str:
                        try:
                            from datetime import datetime, timezone, timedelta
                            tweet_dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
                            now = datetime.now(timezone.utc)
                            age_hours = (now - tweet_dt).total_seconds() / 3600.0
                            if age_hours > 4.0:
                                logger.info(f"Skipping old tweet {link} from @{username} (posted {age_hours:.1f}h ago)")
                                continue
                        except Exception:
                            pass

                    results.append({
                        "id": f"tw_{tweet_id}",
                        "author": username,
                        "title": f"Tweet by @{username}",
                        "text": text.strip(),
                        "url": link,
                        "source_type": "twitter",
                        "has_media": len(media_urls) > 0,
                        "media_urls": media_urls
                    })

            await browser.close()

        return results
