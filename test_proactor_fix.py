import threading
import sys
import io
import asyncio
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def worker():
    print("=== Testing Python 3.14 Windows ProactorEventLoop in Thread ===")
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    async def _test():
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            await context.add_cookies([
                {"name": "auth_token", "value": Config.TWITTER_AUTH_TOKEN, "domain": ".x.com", "path": "/"},
                {"name": "ct0", "value": Config.TWITTER_CT0, "domain": ".x.com", "path": "/"}
            ])
            page = await context.new_page()
            await page.goto("https://x.com/DefiLlama", timeout=20000)
            title = await page.title()
            print(f"✅ PROACTOR SUCCESS inside thread: Loaded title '{title}'")
            await browser.close()

    try:
        loop.run_until_complete(_test())
    finally:
        loop.close()

t = threading.Thread(target=worker)
t.start()
t.join()
