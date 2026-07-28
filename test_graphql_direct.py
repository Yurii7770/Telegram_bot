import requests
import json
import sys
import io
from config import Config

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

auth_token = Config.TWITTER_AUTH_TOKEN
ct0 = Config.TWITTER_CT0

print("=== Testing Direct Twitter GraphQL Endpoints ===")

headers = {
    "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7T244GcvTudu1HeS2BkDtxq2W08g50w5g50w5g50w",
    "x-csrf-token": ct0,
    "cookie": f"auth_token={auth_token}; ct0={ct0}",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "x-twitter-active-user": "yes",
    "x-twitter-auth-type": "OAuth2Session"
}

query_ids = [
    "SoiicK3W5A9Q6L3237T1qg",
    "5V8n9duzy_ZtY8uW-b4Jkw",
    "oB-yMwT5G-GNmWdj0qawWg",
    "SN_5q6k4f0S4K1K5K1K5Kg"
]

for qid in query_ids:
    url = f"https://x.com/i/api/graphql/{qid}/CreateTweet"
    payload = {
        "variables": {
            "tweet_text": "Test tweet",
            "dark_request": False
        },
        "features": {
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "tweetypie_unmention_optimization_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "freedom_of_speech_promoted_execution_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "responsive_web_graphql_skip_user_profile_image_extensions_media_stat_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_enhance_cards_enabled": False
        },
        "fieldToggles": {"withArticleRichContentState": False}
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=5)
        print(f"QueryId {qid}: Status {r.status_code} => {r.text[:120]}")
    except Exception as e:
        print(f"Error {qid}: {e}")
