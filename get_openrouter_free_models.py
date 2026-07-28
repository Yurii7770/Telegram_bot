import requests
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

r = requests.get("https://openrouter.ai/api/v1/models")
if r.status_code == 200:
    data = r.json().get("data", [])
    free_models = [m["id"] for m in data if m.get("pricing", {}).get("prompt") == "0" and m.get("pricing", {}).get("completion") == "0"]
    print(f"Found {len(free_models)} completely free models on OpenRouter:")
    for fm in free_models[:20]:
        print(f" - {fm}")
else:
    print(f"Failed to fetch models: {r.status_code}")
