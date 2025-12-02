import feedparser
import requests
from sqlalchemy.orm import Session
import crud
from datetime import datetime
import re

# ----------------------------------------------
# Strong AI Keywords (Primary Filter)
# ----------------------------------------------
AI_KEYWORDS = [
    "artificial intelligence", "ai", "machine learning",
    "deep learning", "neural", "neural network",
    "generative ai", "gen ai", "foundation model",
    "llm", "large language model", "openai", "chatgpt",
    "anthropic", "claude", "google deepmind",
    "nvidia", "meta ai", "ai model", "ai system",
    "ai startup", "ai tool", "transformer", "nlp",
    "computer vision", "robotics", "autonomous"
]

def is_ai_related(text: str) -> bool:
    """Check for AI relevance using keyword match."""
    if not text:
        return False
    text = text.lower()
    return any(keyword in text for keyword in AI_KEYWORDS)


# ----------------------------------------------
# Clean HTML and Unnecessary Tags
# ----------------------------------------------
def clean_html(raw_html):
    if not raw_html:
        return ""
    clean = re.sub(r"<[^>]+>", "", raw_html)
    clean = clean.replace("&nbsp;", " ").strip()
    return clean


# ----------------------------------------------
# FETCH AND STORE NEWS (Improved Text Extraction)
# ----------------------------------------------
def fetch_and_store_news(db: Session):
    sources = crud.get_active_sources(db)
    new_count = 0

    print(f"🔄 Starting fetch for {len(sources)} sources...")

    HEADERS = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/rss+xml, text/xml, */*"
    }

    for source in sources:
        print(f"📡 Fetching: {source.name}...")

        try:
            response = requests.get(source.url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"   ⚠️ Error {source.name}: Status {response.status_code}")
                continue

            feed = feedparser.parse(response.content)
            if not feed.entries:
                print(f"   ⚠️ Empty feed: {source.name}")
                continue

            for entry in feed.entries[:10]:

                title = clean_html(getattr(entry, "title", ""))
                link = getattr(entry, "link", "")
                summary = clean_html(getattr(entry, "summary", "") or getattr(entry, "description", ""))

                # Extract deeper text (description, content)
                full_text_parts = [title, summary]

                # Some feeds have rich content
                if hasattr(entry, "content"):
                    for c in entry.content:
                        full_text_parts.append(clean_html(c.value))

                # Merge all extracted text
                full_text = " ".join(full_text_parts).strip()

                # Ensure AI relevance
                if not is_ai_related(full_text):
                    print(f"   ⏩ Skipped (Not AI): {title[:50]}")
                    continue

                # Save article
                item = crud.create_news_item(
                    db=db,
                    title=title,
                    summary=summary,
                    url=link,
                    source_id=source.id,
                    published_at=datetime.now()
                )

                if item:
                    new_count += 1
                    print(f"   ✅ Saved AI Article: {title[:60]}...")

        except Exception as e:
            print(f"   ❌ Critical Error in {source.name}: {e}")

    print(f"🏁 Fetch complete. Total saved AI items: {new_count}")
    return new_count
