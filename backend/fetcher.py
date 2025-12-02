import feedparser
import requests
from sqlalchemy.orm import Session
import crud
from datetime import datetime
import re

# ------------------------------------------------------
# 1. AI KEYWORDS FILTER (Strongest possible filtering)
# ------------------------------------------------------
AI_KEYWORDS = [
    "artificial intelligence", "ai", "machine learning",
    "deep learning", "neural network", "generative ai",
    "gen ai", "llm", "large language model",
    "openai", "chatgpt", "anthropic", "claude",
    "google deepmind", "nvidia", "meta ai",
    "ai model", "ai system", "ai startup", "ai tool"
]

def is_ai_related(text: str) -> bool:
    """Return True only if text contains AI keywords."""
    if not text:
        return False
    
    text = text.lower()

    return any(keyword in text for keyword in AI_KEYWORDS)


# ------------------------------------------------------
# 2. FETCH AND STORE NEWS WITH AI-ONLY FILTERING
# ------------------------------------------------------
def fetch_and_store_news(db: Session):
    sources = crud.get_active_sources(db)
    new_count = 0

    print(f"🔄 Starting fetch for {len(sources)} sources...")

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, application/atom+xml, text/xml, */*',
        'Connection': 'keep-alive'
    }

    for source in sources:
        print(f"📡 Fetching: {source.name}...")

        try:
            response = requests.get(source.url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"   ⚠️ Blocked/Error: {source.name} (Status: {response.status_code})")
                continue

            feed = feedparser.parse(response.content)
            if not feed.entries:
                print(f"   ⚠️ Parsed but empty: {source.name}")
                continue

            # Process each entry
            for entry in feed.entries[:10]:  # fetch up to 10 items per source
                title = entry.title
                url = entry.link

                summary = "No summary available."
                if hasattr(entry, 'summary'):
                    summary = entry.summary
                elif hasattr(entry, 'description'):
                    summary = entry.description

                # Clean HTML noise
                clean_text = re.sub("<[^<]+?>", "", summary + " " + title)

                # 🔥 AI FILTERING HERE
                if not is_ai_related(clean_text):
                    print(f"   ⏩ Skipped (Not AI): {title[:40]}")
                    continue

                item = crud.create_news_item(
                    db=db,
                    title=title,
                    summary=summary,
                    url=url,
                    source_id=source.id,
                    published_at=datetime.now()
                )

                if item:
                    new_count += 1
                    print(f"   ✅ Saved AI Article: {title[:45]}...")

        except Exception as e:
            print(f"   ❌ Critical Error {source.name}: {e}")

    print(f"🏁 Fetch complete. Total AI items saved: {new_count}")
    return new_count
