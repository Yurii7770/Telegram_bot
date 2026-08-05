import asyncio
import sys
import io
import os
import requests
from config import Config
from twitter_poster import TwitterPoster

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=== TESTING TWITTER PHOTO ATTACHMENT IN PLAYWRIGHT ===")
poster = TwitterPoster()

# Sample image URL to test
sample_img_url = "https://pbs.twimg.com/media/HOvy2LUWMAAwKYE?format=jpg&name=large"

# Download image to local temp file
temp_file = "temp_test_twitter_upload.jpg"
r = requests.get(sample_img_url, timeout=10)
if r.status_code == 200:
    with open(temp_file, "wb") as f:
        f.write(r.content)
    print(f"Downloaded temp image {temp_file} ({len(r.content)} bytes)")
else:
    print("Failed to download sample image")

# Clean up after test
if os.path.exists(temp_file):
    print("Temp file ready for Playwright upload test")
