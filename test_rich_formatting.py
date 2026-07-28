import sys
import io
import requests
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sample_url = "https://x.com/DuneAnalytics/status/1880000000000000000"

# 3 Rich Formatting Variants using Telegram HTML tags (<b>, <i>, <code>, <a href>)
rich_variants = [
    {
        "name": "VARIANT A: Monospace Tickers/Metrics (<code>$ETH</code>, <code>25%</code>)",
        "title": "⚡ <b>Dune Analytics slashes <code>25%</code> of workforce in <a href=\"{url}\">strategic AI restructuring</a></b>",
        "post_text": "On-chain analytics protocol <b>Dune Analytics</b> is reducing total headcount by <code>25%</code> to reallocate capital toward AI-powered SQL data engines and institutional enterprise services.\n\n• <b>AI Reallocation</b>: Shifting engineering focus toward automated natural-language database queries.\n• <b>Institutional Focus</b>: Expanding enterprise-grade data pipelines for institutional funds and <i>L2 protocols</i>.\n\nThis restructuring underscores a broader shift among Web3 data providers streamlining legacy operations to accelerate AI-native analytics integration."
    },
    {
        "name": "VARIANT B: Italic Strategic Emphasis (<i>italic nuance</i> + <b>bold entities</b>)",
        "title": "⚡ <b>Dune Analytics slashes 25% of staff in <a href=\"{url}\">strategic AI pivot</a></b>",
        "post_text": "On-chain analytics leader <b>Dune Analytics</b> is trimming its workforce by <b>25%</b> to double down on <i>AI-assisted database synthesis</i> and institutional pipeline tools.\n\n• <b>Resource Shift</b>: Accelerating development of <code>natural-language SQL</code> engines.\n• <b>Market Strategy</b>: Target expansion into <i>institutional-grade DeFi & Layer-2</i> data systems.\n\nThe move highlights how leading data providers are adapting lean operational structures to maintain a <i>competitive edge</i> in AI analytics."
    },
    {
        "name": "VARIANT C: Hybrid Premium (<code>Code Stats</code> + <i>Italic Nuance</i> + <b>Bold Highlights</b>)",
        "title": "⚡ <b>Dune Analytics cuts <code>25%</code> of headcount to <a href=\"{url}\">scale enterprise AI infrastructure</a></b>",
        "post_text": "<b>Dune Analytics</b> has initiated a <code>25% headcount reduction</code> as part of a strategic pivot toward <i>AI-driven data products</i> and enterprise solutions.\n\n• <b>AI Engineering</b>: Directing core engineering resources into <code>SQL copilot engines</code>.\n• <b>Enterprise Focus</b>: Strengthening dedicated infrastructure for institutional clients and <i>DeFi treasuries</i>.\n\nThis capital reallocation reflects a maturing market where protocol analytics platforms prioritize automated workflows over headcount expansion."
    }
]

print("=== Sending 3 Rich Formatting Variants to Telegram ===")

for i, var in enumerate(rich_variants, 1):
    title_formatted = var["title"].replace("{url}", sample_url)
    header = f"🎨 <b>[ВАРИАНТ ФОРМАТИРОВАНИЯ #{i}: {var['name']}]</b>\n\n"
    full_msg = f"{header}{title_formatted}\n\n{var['post_text']}"
    
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": Config.ADMIN_CHAT_ID,
        "text": full_msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    r = requests.post(url, json=payload, timeout=10)
    print(f"Rich Variant #{i} sent to Telegram: status={r.status_code}")
