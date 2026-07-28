import sys
import io
import requests
import json
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sample_item = {
    "url": "https://x.com/DuneAnalytics/status/1880000000000000000",
    "author": "DuneAnalytics"
}

# Veteran Professional Style without label tags
veteran_post = {
    "title": "⚡ <b>Dune Analytics slashes 25% of workforce in <a href=\"{url}\">strategic AI restructuring</a></b>",
    "post_text": "On-chain data giant <b>Dune Analytics</b> is reducing headcount by <b>25%</b> to reallocate capital toward AI-powered SQL engines and enterprise infrastructure.\n\n• <b>AI Reallocation</b>: Shifting engineering focus toward automated natural-language queries.\n• <b>Institutional Focus</b>: Expanding enterprise-grade data pipelines for institutional funds and protocols.\n\nThis restructuring underscores a broader shift among Web3 data providers streamlining legacy operations to accelerate AI-native analytics integration."
}

title_formatted = veteran_post["title"].replace("{url}", sample_item["url"])
header = "👔 <b>[ПРОФЕСІЙНИЙ ВЕТЕРАНСЬКИЙ СТИЛЬ — БЕЗ ШТУЧНИХ ЗАГОЛОВКІВ]</b>\n\n"
full_msg = f"{header}{title_formatted}\n\n{veteran_post['post_text']}"

url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": Config.ADMIN_CHAT_ID,
    "text": full_msg,
    "parse_mode": "HTML",
    "disable_web_page_preview": False
}
r = requests.post(url, json=payload, timeout=10)
print(f"Veteran style option sent to Telegram: status={r.status_code}")
