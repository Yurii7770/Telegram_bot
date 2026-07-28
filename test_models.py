import sys
import io
from openai import OpenAI
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

client = OpenAI(base_url=Config.OPENROUTER_BASE_URL, api_key=Config.OPENROUTER_API_KEY)

test_models = [
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "openai/gpt-oss-20b:free",
    "inclusionai/ling-3.0-flash:free",
    "openrouter/free"
]

print("=== Testing Active Free Models ===")
for model in test_models:
    try:
        res = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Respond strictly in JSON: {\"status\": \"OK\"}"}],
            max_tokens=60,
            timeout=10
        )
        content = res.choices[0].message.content
        print(f"✅ SUCCESS {model}: '{content.strip() if content else 'EMPTY'}'")
    except Exception as e:
        print(f"❌ FAIL {model}: {e}")
