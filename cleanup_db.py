import sqlite3
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect("bot_data.db")
cursor = conn.cursor()

# Delete records where status was SKIP due to AI errors
cursor.execute("DELETE FROM processed_tweets WHERE details LIKE '%JSON%' OR details LIKE '%Empty%' OR details LIKE '%error%'")
deleted_count = cursor.rowcount
conn.commit()

print(f"Cleaned up {deleted_count} faulty SKIP records from database.")
conn.close()
