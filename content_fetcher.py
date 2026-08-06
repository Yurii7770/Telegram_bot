import logging
import requests
import bs4
import hashlib
import urllib.parse
import sys
import asyncio
import re
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
        failed_accounts = []
        max_age_hours = getattr(Config, "MAX_TWEET_AGE_HOURS", 10.0)

        async with async_playwright() as p:
            # Low-memory launch flags optimized for 512MB RAM cloud environments & VPS
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

            # Block heavy media & font asset downloads to save up to 80% RAM during DOM parsing
            await context.route(
                "**/*",
                lambda route: route.abort() if route.request.resource_type in ["media", "font"] else route.continue_()
            )

            # Inject cookies if present
            if self.auth_token and self.ct0:
                cookies = [
                    {"name": "auth_token", "value": self.auth_token, "domain": ".x.com", "path": "/", "secure": True, "sameSite": "Lax"},
                    {"name": "ct0", "value": self.ct0, "domain": ".x.com", "path": "/", "secure": True, "sameSite": "Lax"},
                    {"name": "auth_token", "value": self.auth_token, "domain": ".twitter.com", "path": "/", "secure": True, "sameSite": "Lax"},
                    {"name": "ct0", "value": self.ct0, "domain": ".twitter.com", "path": "/", "secure": True, "sameSite": "Lax"}
                ]
                if self.twid:
                    cookies.append({"name": "twid", "value": self.twid, "domain": ".x.com", "path": "/", "secure": True, "sameSite": "Lax"})
                    cookies.append({"name": "twid", "value": self.twid, "domain": ".twitter.com", "path": "/", "secure": True, "sameSite": "Lax"})
                await context.add_cookies(cookies)

            for username in usernames:
                page = None
                account_fetched = False
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

                        img_els = await el.query_selector_all('div[data-testid="tweetPhoto"] img, div[data-testid*="card"] img, img[src*="pbs.twimg.com/media/"], img[src*="pbs.twimg.com/card_img/"]')
                        media_urls = []
                        for img in img_els:
                            src = await img.get_attribute("src")
                            if src and ("media" in src or "card_img" in src or "twimg.com" in src):
                                # Upgrade quality to name=large for high-res Twitter images
                                if "name=" in src:
                                    src = re.sub(r'name=[a-zA-Z0-9_]+', 'name=large', src)
                                elif "format=" in src and "name=" not in src:
                                    src += "&name=large"
                                elif "pbs.twimg.com/media/" in src and "?" not in src:
                                    src += "?format=jpg&name=large"
                                if src not in media_urls and not src.endswith(".svg"):
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
                    if count > 0:
                        account_fetched = True
                except Exception as e:
                    logger.warning(f"Playwright tweet fetch failed for @{username}: {e}")
                finally:
                    if page:
                        await page.close()

                if not account_fetched:
                    failed_accounts.append(username)

            await browser.close()

        # Fallback for accounts where Playwright returned 0 items (e.g. missing cookies or cloud IP restrictions)
        if failed_accounts:
            logger.info(f"Attempting Nitter/RSS fallback fetch for {len(failed_accounts)} accounts with 0 Playwright tweets: {failed_accounts}")
            fallback_items = self._fetch_via_nitter_fallback(failed_accounts, limit_per_account=limit, max_age_hours=max_age_hours)
            all_results.extend(fallback_items)

        # Sort all fetched tweets strictly from NEWEST (highest timestamp) to OLDEST
        all_results.sort(key=lambda x: x.get("timestamp", 0.0), reverse=True)
        logger.info(f"Sorted {len(all_results)} total tweets strictly from NEWEST to OLDEST")

        return all_results

    def _fetch_via_nitter_fallback(self, usernames: List[str], limit_per_account: int = 5, max_age_hours: float = 10.0) -> List[Dict]:
        """Fallback fetcher using Nitter RSS instances if Playwright is blocked or lacks cookies on Cloud server."""
        nitter_instances = [
            "https://nitter.net",
            "https://nitter.poast.org",
            "https://nitter.privacydev.net"
        ]
        results = []
        now = datetime.now(timezone.utc)

        for username in usernames:
            fetched = False
            for instance in nitter_instances:
                if fetched:
                    break
                try:
                    rss_url = f"{instance}/{username}/rss"
                    resp = self.session.get(rss_url, timeout=8)
                    if resp.status_code == 200 and resp.text:
                        soup = bs4.BeautifulSoup(resp.text, 'xml')
                        items = soup.find_all('item')
                        count = 0
                        for item in items[:limit_per_account]:
                            link = item.find('link').text.strip() if item.find('link') else ""
                            description = item.find('description').text.strip() if item.find('description') else ""
                            pub_date = item.find('pubDate').text.strip() if item.find('pubDate') else ""
                            
                            # Clean HTML description to plain text & extract images
                            desc_soup = bs4.BeautifulSoup(description, 'html.parser')
                            clean_text = desc_soup.get_text().strip()
                            img_tags = desc_soup.find_all('img')
                            media_urls = []
                            for img in img_tags:
                                img_src = img.get('src', '')
                                if img_src:
                                    if img_src.startswith('/'):
                                        img_src = f"{instance}{img_src}"
                                    if img_src not in media_urls and not img_src.endswith(".svg"):
                                        media_urls.append(img_src)
                            
                            tweet_id = link.split('/status/')[-1].split('#')[0] if '/status/' in link else ""
                            if not tweet_id:
                                continue

                            tweet_url = f"https://x.com/{username}/status/{tweet_id}"
                            tweet_timestamp = 0.0

                            if pub_date:
                                try:
                                    # Example pubDate: 'Thu, 30 Jul 2026 08:00:00 GMT'
                                    dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S GMT').replace(tzinfo=timezone.utc)
                                    tweet_timestamp = dt.timestamp()
                                    age_hours = (now - dt).total_seconds() / 3600.0
                                    if age_hours > max_age_hours:
                                        continue
                                except Exception:
                                    pass

                            results.append({
                                "id": f"tw_{tweet_id}",
                                "author": username,
                                "title": f"Tweet by @{username}",
                                "text": clean_text,
                                "url": tweet_url,
                                "source_type": "twitter_fallback",
                                "has_media": len(media_urls) > 0,
                                "media_urls": media_urls,
                                "timestamp": tweet_timestamp
                            })
                            count += 1

                        logger.info(f"Fallback RSS fetched {count} tweets for @{username} via {instance}")
                        fetched = True
                except Exception as e:
                    logger.debug(f"Nitter fallback {instance} failed for @{username}: {e}")

        return results
