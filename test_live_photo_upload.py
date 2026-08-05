import asyncio
import sys
import io
import requests
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

async def main():
    from playwright.async_api import async_playwright
    print("=== Fetching real live tweet photo and uploading to Telegram ===")
    
    photo_url = None
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = await context.new_page()
        await page.goto("https://x.com/Lookonchain", timeout=25000)
        await page.wait_for_timeout(3500)
        
        img_els = await page.query_selector_all('div[data-testid="tweetPhoto"] img')
        for img in img_els:
            src = await img.get_attribute("src")
            if src and "media" in src:
                photo_url = src
                break
        await browser.close()

    print(f"Extracted real photo URL: {photo_url}")
    if photo_url:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r_img = requests.get(photo_url, headers=headers, timeout=10)
        print(f"Image download status: {r_img.status_code}, Bytes: {len(r_img.content)}")
        
        if r_img.status_code == 200:
            tg_url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendPhoto"
            files = {"photo": ("tweet_image.jpg", r_img.content, "image/jpeg")}
            data = {
                "chat_id": Config.ADMIN_CHAT_ID,
                "caption": "📸 <b>LIVE REAL PHOTO FROM TWITTER!</b>\n\nDirectly uploaded from @Lookonchain tweet.",
                "parse_mode": "HTML"
            }
            tg_resp = requests.post(tg_url, data=data, files=files, timeout=15)
            print(f"Telegram upload status: {tg_resp.status_code}")
            print(f"Telegram response: {tg_resp.text}")

asyncio.run(main())
