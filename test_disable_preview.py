import requests
import sys
import io
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

bot_token = Config.TELEGRAM_BOT_TOKEN
admin_chat_id = Config.ADMIN_CHAT_ID

title = "🚨 <b>BREAKING: DefiLlama Cuts Ties With DL News <a href='https://beincrypto.com'>Mystery Ownership Sale</a></b>"
post_text = "💥 <b>DefiLlama</b> has severed its partnership with DL News following an undisclosed transaction.\n\n📌 <b>Key Highlights:</b>\n• <b>Transition:</b> Ownership mystery.\n\nThis move reinforces transparency."

header = "🎨 <b>[ТЕСТ: БЕЗ БОЛЬШОГО ПРЕВЬЮ ССЫЛКИ ВНИЗУ]</b>\n\n"
full_msg = f"{header}{title}\n\n{post_text}"

payload = {
    "chat_id": admin_chat_id,
    "text": full_msg,
    "parse_mode": "HTML",
    "disable_web_page_preview": True,
    "link_preview_options": {"is_disabled": True}
}

r = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json=payload)
print(f"Disabled preview test sent: status={r.status_code}, response={r.json()}")
