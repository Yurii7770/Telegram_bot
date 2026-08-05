import asyncio
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def main():
    print("=== Testing Strict Direct Twitter Tweet Extractor ===")
    from playwright.async_api import async_playwright
    from config import Config

    target_accounts = ["DefiLlama", "Lookonchain", "ArkhamIntel", "vitalikbuterin", "CoinbaseMarkets", "elonmusk"]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900}
        )

        if Config.TWITTER_AUTH_TOKEN and Config.TWITTER_CT0:
            await context.add_cookies([
                {"name": "auth_token", "value": Config.TWITTER_AUTH_TOKEN, "domain": ".x.com", "path": "/"},
                {"name": "ct0", "value": Config.TWITTER_CT0, "domain": ".x.com", "path": "/"}
            ])

        for username in target_accounts:
            page = None
            try:
                page = await context.new_page()
                target_url = f"https://x.com/{username}"
                await page.goto(target_url, timeout=25000)
                await page.wait_for_timeout(3000)
                # Scroll slightly to trigger virtual list loading
                await page.evaluate("window.scrollBy(0, 300)")
                await page.wait_for_timeout(1000)

                tweet_elements = await page.query_selector_all('article[data-testid="tweet"]')
                print(f"\n@{username}: Found {len(tweet_elements)} tweet articles")

                for idx, el in enumerate(tweet_elements[:3]):
                    link_el = await el.query_selector('a[href*="/status/"]')
                    link = await link_el.get_attribute("href") if link_el else ""
                    if link and not link.startswith("http"):
                        link = f"https://x.com{link}"

                    text_el = await el.query_selector('div[data-testid="tweetText"]')
                    text = await text_el.inner_text() if text_el else ""

                    print(f"   [{idx+1}] Direct URL: {link}")
                    print(f"       Text: '{text[:60]}...'")

            except Exception as e:
                print(f"@{username} Error: {e}")
            finally:
                if page:
                    await page.close()

        await browser.close()

asyncio.run(main())
