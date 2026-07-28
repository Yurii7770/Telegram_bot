import sqlite3
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect("bot_data.db")
cursor = conn.cursor()

cursor.execute("SELECT id, author, title, has_media, media_urls FROM pending_posts ORDER BY id DESC LIMIT 15")
rows = cursor.fetchall()

print("=== MEDIA CHECK IN PENDING POSTS ===")
for r in rows:
    print(f"ID: {r[0]}, Author: {r[1]}, has_media: {r[3]}, media_urls: {r[4]}")
    print(f"Title: {r[2][:70]}...\n")

conn.close()
