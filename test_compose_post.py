import asyncio
import sys
import io
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def main():
    print("=== Testing Direct Twitter Compose Dialog ===")
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900}
        )
        await context.add_cookies([
            {"name": "auth_token", "value": Config.TWITTER_AUTH_TOKEN, "domain": ".x.com", "path": "/"},
            {"name": "ct0", "value": Config.TWITTER_CT0, "domain": ".x.com", "path": "/"},
            {"name": "twid", "value": Config.TWITTER_TWID, "domain": ".x.com", "path": "/"}
        ])
        page = await context.new_page()
        print("Navigating to https://x.com/compose/post...")
        await page.goto("https://x.com/compose/post", timeout=30000)
        await page.wait_for_timeout(4000)
        
        print(f"URL: {page.url}")
        print(f"Title: {await page.title()}")
        
        buttons = await page.query_selector_all('button, div[role="button"]')
        print(f"Found {len(buttons)} interactive buttons/elements.")
        for idx, btn in enumerate(buttons):
            testid = await btn.get_attribute("data-testid")
            btn_text = await btn.inner_text()
            if testid or ("Post" in btn_text or "Reply" in btn_text):
                print(f"Button [{idx}]: testid='{testid}', text='{btn_text.strip()[:30]}'")
                
        await browser.close()

asyncio.run(main())
