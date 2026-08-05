import asyncio
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def debug():
    from playwright.async_api import async_playwright
    from config import Config

    print("=== Debugging Playwright Twitter Page Loading ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Test 1: With cookies from .env
        context1 = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        await context1.add_cookies([
            {"name": "auth_token", "value": Config.TWITTER_AUTH_TOKEN, "domain": ".x.com", "path": "/"},
            {"name": "ct0", "value": Config.TWITTER_CT0, "domain": ".x.com", "path": "/"}
        ])
        page1 = await context1.new_page()
        print("Navigating WITH cookies...")
        await page1.goto("https://x.com/DefiLlama", timeout=20000)
        await page1.wait_for_timeout(3000)
        
        title1 = await page1.title()
        tweets1 = await page1.query_selector_all('article[data-testid="tweet"]')
        cell_items1 = await page1.query_selector_all('div[data-testid="cellInnerDefinition"]')
        print(f"WITH Cookies -> Title: '{title1}', Tweets (article): {len(tweets1)}, cellInnerDefinition: {len(cell_items1)}")
        
        # Check if redirected to login
        url1 = page1.url
        print(f"Final URL 1: {url1}")

        # Test 2: WITHOUT cookies
        context2 = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page2 = await context2.new_page()
        print("\nNavigating WITHOUT cookies...")
        await page2.goto("https://x.com/DefiLlama", timeout=20000)
        await page2.wait_for_timeout(3000)
        
        title2 = await page2.title()
        tweets2 = await page2.query_selector_all('article[data-testid="tweet"]')
        cell_items2 = await page2.query_selector_all('div[data-testid="cellInnerDefinition"]')
        print(f"WITHOUT Cookies -> Title: '{title2}', Tweets (article): {len(tweets2)}, cellInnerDefinition: {len(cell_items2)}")
        print(f"Final URL 2: {page2.url}")
        
        await browser.close()

asyncio.run(debug())
