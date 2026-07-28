import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

modules = ["twikit", "playwright", "selenium", "tweepy", "curl_cffi"]
print("=== Python Dependencies Check ===")
for mod in modules:
    try:
        __import__(mod)
        print(f"OK: {mod}: Installed")
    except ImportError:
        print(f"NO: {mod}: Not installed")
