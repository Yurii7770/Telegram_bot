import sys
import io
from config import Config
from ai_editor import AIEditor

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ai = AIEditor(Config.OPENROUTER_API_KEY, Config.OPENROUTER_MODEL, Config.OPENROUTER_BASE_URL)

sample_item = {
    "url": "https://x.com/DefiLlama/status/18123456789",
    "author": "DefiLlama",
    "title": "Обновление протокола DeFi Llama",
    "text": "Мы запустили новую аналитическую панель для отслеживания TVL в сетях L2 Arbitrum и Optimism."
}

print("=== Testing AI Editor English Prompt ===")
result = ai.process_item(sample_item)
print("Result Status:", result.get("status"))
print("Title:", result.get("title"))
print("Post Text:\n", result.get("post_text"))
