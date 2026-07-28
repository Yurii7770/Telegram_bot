import sqlite3
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect("bot_data.db")
cursor = conn.cursor()

print("--- PENDING POSTS ---")
cursor.execute("SELECT id, tweet_id, author, title, post_text, status, created_at FROM pending_posts ORDER BY id DESC LIMIT 10")
rows = cursor.fetchall()
for r in rows:
    print(f"ID: {r[0]}, TweetID: {r[1]}, Author: {r[2]}, Status: {r[5]}, Created: {r[6]}")
    print(f"Title: {r[3]}")
    print(f"Text snippet: {r[4][:150]}...\n")

print("--- PROCESSED TWEETS ---")
cursor.execute("SELECT tweet_id, author, status, details, processed_at FROM processed_tweets ORDER BY processed_at DESC LIMIT 10")
rows2 = cursor.fetchall()
for r in rows2:
    print(r)

conn.close()
