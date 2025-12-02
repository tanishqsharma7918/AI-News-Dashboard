import feedparser
import requests
from sqlalchemy.orm import Session
import crud
from datetime import datetime
import re

# ============================================================
# AI DETECTION — SMART TITLE-FOCUSED (MUCH MORE ACCURATE)
# ============================================================

TITLE_KEYWORDS = [
    "ai", "a.i",
    "ml", "machine learning",
    "deep learning", "neural",
    "model", "models",
    "llm", "large language model",
    "agent", "agents",
    "nvidia", "gpu", "gpus",
    "openai", "anthropic", "claude",
    "google", "deepmind", "meta",
    "transformer", "diffusion",
    "embedding", "embeddings",
    "training", "inference",
    "benchmark", "research", "study",
]

# Secondary keywords from summary/content
AI_KEYWORDS = [
    r"\bai\b",
    r"\bartificial intelligence\b",
    r"\bmachine learning\b",
    r"\bdeep learning\b",
    r"\btransformer\b",
    r"\bneural\b",
    r"\bllm\b",
    r"\bgenerative\b",
    r"\bgenerative ai\b",
    r"\bgen ai\b",
    r"\bmodel\b",
    r"\bmodels\b",
    r"\bweights\b",
    r"\bparameters\b",
    r"\bembedding\b",
]

# ============================================================
# EXCLUSION PATTERNS (balanced)
# ============================================================

# ❗ These block junk from Reddit (but NOT research)
EXCLUDE_PATTERNS = [
    r"who('?s)? hiring",
    r"who wants to be hired",
    r"automoderator",
    r"megathread",
    r"monthly thread",
    r"self[- ]?promotion",
    r"hiring",
    r"job opening",
    r"salary",
    r"consulting",
]

def matches_any(patterns, text):
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def is_ai_related(title: str, summary: str) -> bool:
    """Corrected & balanced — accepts real AI content, blocks junk."""
    if not title:
        return False

    title_l = title.lower()
    summary_l = summary.lower()

    # --- HARD EXCLUSIONS ---
    if matches_any(EXCLUDE_PATTERNS, title_l + " " + summary_l):
        return False

    # --- PRIORITY: TITLE MATCH ---
    if any(k in title_l for k in TITLE_KEYWORDS):
        return True

    # --- FALLBACK: SUMMARY KEYWORDS ---
    if matches_any(AI_KEYWORDS, summary_l):
        return True

    return False

# ============================================================
# CLEAN HTML
# ============================================================

def clean_html(raw_html):
    if not raw_html:
        return ""
    clean = re.sub(r"<[^>]+>", "", raw_html)
    clean = re.sub(r"\s+", " ", clean)
    return clean.strip()

# ============================================================
# MAIN FETCHER LOGIC
# ============================================================

def fetch_and_store_news(db: Session):
    sources = crud.get_active_sources(db)
    new_count = 0

    print(f"\n🔄 Fetching from {len(sources)} sources...\n")

    HEADERS = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/rss+xml,text/xml,*/*"
    }

    for source in sources:
        print(f"\n📡 Source: {source.name}")

        try:
            response = requests.get(source.url, headers=HEADERS, timeout=12)

            if response.status_code != 200:
                print(f"⚠️ HTTP {response.status_code}")
                continue

            feed = feedparser.parse(response.content)

            if not feed.entries:
                print("⚠️ No entries returned from feed")
                continue

            for entry in feed.entries[:25]:  # Fetch more items
                title = clean_html(getattr(entry, "title", ""))
                link = getattr(entry, "link", "")
                summary = clean_html(
                    getattr(entry, "summary", "") or
                    getattr(entry, "description", "")
                )

                # Include full content if provided
                parts = [title, summary]
                if hasattr(entry, "content"):
                    for c in entry.content:
                        parts.append(clean_html(c.value))

                full_summary = " ".join(parts)

                # Filter NON-AI posts
                if not is_ai_related(title, full_summary):
                    print(f"   ⏩ Skipped: {title[:70]}")
                    continue

                # Skip duplicates
                if crud.news_exists(db, link):
                    print(f"   ⚪ Duplicate: {title[:70]}")
                    continue

                # Store item
                item = crud.create_news_item(
                    db=db,
                    title=title,
                    summary=summary or title,
                    url=link,
                    source_id=source.id,
                    published_at=datetime.now(),
                )

                if item:
                    new_count += 1
                    print(f"   ✅ Saved: {title[:80]}")

        except Exception as e:
            print(f"❌ Error in {source.name}: {e}")

    print(f"\n🏁 Done. Saved {new_count} new items.\n")
    return new_count
