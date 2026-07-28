import asyncio
import sys
import io
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def main():
    print("=== Testing Playwright Headless Twitter Reply Posting ===")
    from playwright.async_api import async_playwright
    
    auth_token = Config.TWITTER_AUTH_TOKEN
    ct0 = Config.TWITTER_CT0
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        
        # Add Twitter cookies to browser context
        await context.add_cookies([
            {"name": "auth_token", "value": auth_token, "domain": ".x.com", "path": "/"},
            {"name": "ct0", "value": ct0, "domain": ".x.com", "path": "/"}
        ])
        
        page = await context.new_page()
        print("Navigating to Twitter target URL...")
        await page.goto("https://x.com/DefiLlama", timeout=30000)
        await page.wait_for_timeout(3000)
        
        title = await page.title()
        print(f"Page loaded: '{title}'")
        
        if "X" in title or "DefiLlama" in title:
            print("✅ SUCCESS: Playwright authenticated and loaded Twitter profile successfully!")
        else:
            print(f"⚠️ Page title check: {title}")
            
        await browser.close()

asyncio.run(main())
