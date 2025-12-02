import feedparser
import requests
from sqlalchemy.orm import Session
import crud
from datetime import datetime
import re

# ----------------------------------------------
# AI KEYWORDS (safe, word-boundary matched)
# ----------------------------------------------
AI_KEYWORDS = [
    r"\bai\b",
    r"\bartificial intelligence\b",
    r"\bmachine learning\b",
    r"\bdeep learning\b",
    r"\bneural network\b",
    r"\bcomputer vision\b",
    r"\bnlp\b",
    r"\btransformer\b",
    r"\bllm\b",
    r"\blarge language model\b",
    r"\bgen ai\b",
    r"\bgenerative ai\b",
    r"\bchatgpt\b",
    r"\bopenai\b",
    r"\banthropic\b",
    r"\bclaude\b",
    r"\bnvidia\b",
    r"\bmeta ai\b",
    r"\bgoogle ai\b",
]

# ----------------------------------------------
# EXCLUSION LIST for junk threads
# ----------------------------------------------
EXCLUDE_PATTERNS = [
    r"self[- ]?promotion",
    r"who('?s)? hiring",
    r"who wants to be hired",
    r"automoderator",
    r"reddit",
    r"monthly thread",
    r"megathread",
    r"community thread",
    r"hiring thread",
    r"job\b",
    r"resume\b",
    r"\[d\]",
]


def matches_any(patterns, text):
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def is_ai_related(text: str) -> bool:
    """AI filtering with correct word boundaries & first blocking Reddit junk."""
    if not text:
        return False

    text = text.lower().strip()

    # ❌ HARD BLOCK meta/reddit/junk
    if matches_any(EXCLUDE_PATTERNS, text):
        return False

    # ✅ TRUE AI keyword detection
    return matches_any(AI_KEYWORDS, text)


# ----------------------------------------------
# Clean HTML
# ----------------------------------------------
def clean_html(raw_html):
    if not raw_html:
        return ""
    clean = re.sub(r"<[^>]+>", "", raw_html)  # remove tags
    clean = re.sub(r"\s+", " ", clean)        # normalize whitespace
    return clean.strip()


# ----------------------------------------------
# Fetch + Filter + Save
# ----------------------------------------------
def fetch_and_store_news(db: Session):
    sources = crud.get_active_sources(db)
    new_count = 0

    print(f"🔄 Starting fetch from {len(sources)} sources...\n")

    HEADERS = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/rss+xml,text/xml,*/*"
    }

    for source in sources:
        print(f"📡 Fetching: {source.name}")

        try:
            response = requests.get(source.url, headers=HEADERS, timeout=10)

            if response.status_code != 200:
                print(f"⚠️  Error fetching {source.name}: HTTP {response.status_code}")
                continue

            feed = feedparser.parse(response.content)

            if not feed.entries:
                print(f"⚠️  No entries in feed: {source.name}")
                continue

            for entry in feed.entries[:15]:  # read 15 entries for safety
                title = clean_html(getattr(entry, "title", ""))
                link = getattr(entry, "link", "")
                summary = clean_html(
                    getattr(entry, "summary", "") or
                    getattr(entry, "description", "")
                )

                parts = [title, summary]

                if hasattr(entry, "content"):
                    for c in entry.content:
                        parts.append(clean_html(c.value))

                full_text = " ".join(parts).lower().strip()

                # 🚫 FILTER NON-AI
                if not is_ai_related(full_text):
                    print(f"   ⏩ Skipped (Not AI): {title[:60]}")
                    continue

                # 🚫 skip if already exists
                if crud.news_exists(db, link):
                    continue

                # ✅ Save article
                item = crud.create_news_item(
                    db=db,
                    title=title,
                    summary=summary or title,
                    url=link,
                    source_id=source.id,
                    published_at=datetime.now()
                )

                if item:
                    new_count += 1
                    print(f"   ✅ Saved AI News: {title[:80]}")

        except Exception as e:
            print(f"❌ Critical fetch error in {source.name}: {e}")

    print(f"\n🏁 Fetch Done. Total Saved: {new_count}\n")
    return new_count
