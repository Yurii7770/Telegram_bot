import logging
import requests
import bs4
import hashlib
import urllib.parse
import sys
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timezone
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
        Fetches posts STRICTLY and 100% ONLY from Twitter (X) target accounts,
        sorted strictly from NEWEST to OLDEST.
        """
        logger.info(f"Fetching tweets strictly from {len(twitter_accounts)} target Twitter accounts...")
        all_items = self._fetch_all_via_playwright(twitter_accounts, limit_per_account=5)
        logger.info(f"Total Twitter content items fetched: {len(all_items)}")
        return all_items

    def get_twitter_posts(self, username: str, limit: int = 5) -> List[Dict]:
        """Single account fetch helper."""
        return self._fetch_all_via_playwright([username], limit_per_account=limit)

    def _fetch_all_via_playwright(self, twitter_accounts: List[str], limit_per_account: int = 5) -> List[Dict]:
        """Uses a single Playwright Chromium session to fetch tweets across target handles efficiently."""
        if not twitter_accounts:
            return []

        if sys.platform == "win32":
            loop = asyncio.ProactorEventLoop()
        else:
            loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._async_batch_playwright_fetch(twitter_accounts, limit_per_account))
        except Exception as e:
            logger.error(f"Error in batch Playwright fetch: {e}")
            return []
        finally:
            loop.close()

    async def _async_batch_playwright_fetch(self, usernames: List[str], limit: int = 5) -> List[Dict]:
        from playwright.async_api import async_playwright

        all_results = []
        max_age_hours = getattr(Config, "MAX_TWEET_AGE_HOURS", 10.0)

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

            for username in usernames:
                page = None
                try:
                    page = await context.new_page()
                    target_url = f"https://x.com/{username}"
                    await page.goto(target_url, timeout=20000)
                    await page.wait_for_timeout(2500)
                    # Scroll slightly to trigger virtual list loading on Twitter SPA
                    await page.evaluate("window.scrollBy(0, 300)")
                    await page.wait_for_timeout(1000)

                    tweet_elements = await page.query_selector_all('article[data-testid="tweet"]')
                    count = 0
                    for el in tweet_elements[:limit]:
                        link_el = await el.query_selector('a[href*="/status/"]')
                        link = await link_el.get_attribute("href") if link_el else ""
                        if link and not link.startswith("http"):
                            link = f"https://x.com{link}"

                        text_el = await el.query_selector('div[data-testid="tweetText"]')
                        text = await text_el.inner_text() if text_el else ""

                        img_els = await el.query_selector_all('div[data-testid="tweetPhoto"] img')
                        media_urls = []
                        for img in img_els:
                            src = await img.get_attribute("src")
                            if src and "media" in src:
                                media_urls.append(src)

                        if link and text and "/status/" in link:
                            tweet_id = link.split("/status/")[-1].split("?")[0]

                            time_el = await el.query_selector('time')
                            datetime_str = await time_el.get_attribute('datetime') if time_el else ""
                            tweet_timestamp = 0.0
                            if datetime_str:
                                try:
                                    tweet_dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
                                    tweet_timestamp = tweet_dt.timestamp()
                                    now = datetime.now(timezone.utc)
                                    age_hours = (now - tweet_dt).total_seconds() / 3600.0
                                    if age_hours > max_age_hours:
                                        logger.info(f"Skipping old tweet {link} from @{username} (posted {age_hours:.1f}h ago > {max_age_hours}h limit)")
                                        continue
                                except Exception:
                                    pass

                            all_results.append({
                                "id": f"tw_{tweet_id}",
                                "author": username,
                                "title": f"Tweet by @{username}",
                                "text": text.strip(),
                                "url": link,
                                "source_type": "twitter",
                                "has_media": len(media_urls) > 0,
                                "media_urls": media_urls,
                                "timestamp": tweet_timestamp
                            })
                            count += 1

                    logger.info(f"Fetched {count} tweets for @{username} via Playwright (URL: {target_url})")
                except Exception as e:
                    logger.warning(f"Playwright tweet fetch failed for @{username}: {e}")
                finally:
                    if page:
                        await page.close()

            await browser.close()

        # Sort all fetched tweets strictly from NEWEST (highest timestamp) to OLDEST
        all_results.sort(key=lambda x: x.get("timestamp", 0.0), reverse=True)
        logger.info(f"Sorted {len(all_results)} total tweets strictly from NEWEST to OLDEST")

        return all_results
