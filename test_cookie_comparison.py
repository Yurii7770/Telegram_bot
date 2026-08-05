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
        
        # Test A: With .env cookies
        ctx_a = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        await ctx_a.add_cookies([
            {"name": "auth_token", "value": Config.TWITTER_AUTH_TOKEN, "domain": ".x.com", "path": "/", "secure": True},
            {"name": "ct0", "value": Config.TWITTER_CT0, "domain": ".x.com", "path": "/", "secure": True}
        ])
        page_a = await ctx_a.new_page()
        await page_a.goto("https://x.com/DefiLlama", timeout=20000)
        await page_a.wait_for_timeout(3000)
        tweets_a = await page_a.query_selector_all('article[data-testid="tweet"]')
        print(f"Test A (WITH .env cookies) -> Tweets: {len(tweets_a)}, Final URL: {page_a.url}")
        
        # Test B: Without cookies
        ctx_b = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page_b = await ctx_b.new_page()
        await page_b.goto("https://x.com/DefiLlama", timeout=20000)
        await page_b.wait_for_timeout(3000)
        tweets_b = await page_b.query_selector_all('article[data-testid="tweet"]')
        print(f"Test B (WITHOUT cookies) -> Tweets: {len(tweets_b)}, Final URL: {page_b.url}")

        await browser.close()

asyncio.run(main())
