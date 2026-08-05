import asyncio
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def main():
    from playwright.async_api import async_playwright
    from config import Config

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900}
        )

        if Config.TWITTER_AUTH_TOKEN and Config.TWITTER_CT0:
            await context.add_cookies([
                {"name": "auth_token", "value": Config.TWITTER_AUTH_TOKEN, "domain": ".x.com", "path": "/", "secure": True},
                {"name": "ct0", "value": Config.TWITTER_CT0, "domain": ".x.com", "path": "/", "secure": True}
            ])

        page = await context.new_page()
        
        # Test accounts
        accounts = ["DefiLlama", "Lookonchain", "vitalikbuterin", "CoinbaseMarkets", "elonmusk"]

        for username in accounts:
            print(f"\n--- Testing @{username} ---")
            await page.goto(f"https://x.com/{username}", timeout=25000)
            await page.wait_for_timeout(3500)
            
            # Check for articles
            articles = await page.query_selector_all('article[data-testid="tweet"]')
            if not articles:
                # Try scrolling down 500px to trigger lazy load
                await page.evaluate("window.scrollBy(0, 500)")
                await page.wait_for_timeout(2000)
                articles = await page.query_selector_all('article[data-testid="tweet"]')
            
            print(f"Articles count for @{username}: {len(articles)}")
            for a in articles[:3]:
                link_el = await a.query_selector('a[href*="/status/"]')
                link = await link_el.get_attribute("href") if link_el else ""
                text_el = await a.query_selector('div[data-testid="tweetText"]')
                text = await text_el.inner_text() if text_el else ""
                print(f"   -> Link: https://x.com{link} | Text: '{text[:50]}...'")

        await browser.close()

asyncio.run(main())
