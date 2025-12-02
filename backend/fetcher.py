import feedparser
import requests
from sqlalchemy.orm import Session
import crud
from datetime import datetime
import re

# ============================================================
# AI DETECTION — BALANCED & SMART
# ============================================================

AI_KEYWORDS = [
    r"\bai\b",
    r"\bartificial intelligence\b",
    r"\bmachine learning\b",
    r"\bdeep learning\b",
    r"\bneural\b",
    r"\bneural network\b",
    r"\bcomputer vision\b",
    r"\btransformer\b",
    r"\bgenerative\b",
    r"\bgenerative ai\b",
    r"\bgen ai\b",
    r"\bllm\b",
    r"\bmodel\b",
    r"\bmodels\b",
    r"\bembedding\b",
    r"\btoken\b",
    r"\btraining\b",
    r"\binference\b",
    r"\blarge language model\b",
    # Company/Tech specific
    r"\bopenai\b",
    r"\bchatgpt\b",
    r"\banthropic\b",
    r"\bclaude\b",
    r"\bnvidia\b",
    r"\bmeta\b",
    r"\balphafold\b",
    r"\bdeepmind\b",
    r"\bgoogle ai\b",
    r"\bmicrosoft ai\b",
]

# ============================================================
# EXCLUSION PATTERNS (balanced)
# ============================================================

EXCLUDE_PATTERNS = [
    r"who('?s)? hiring",
    r"who wants to be hired",
    r"automoderator",
    r"megathread",
    r"monthly thread",
    r"hiring thread",
    r"self[- ]?promotion",
    r"\bjob(s)?\b",
    r"\bresume\b",
    r"looking for work",
    r"\bhiring\b",
    r"salary",
    r"consulting",
    # DO NOT BLOCK "[D]" — research uses it
    # DO NOT block "reddit" globally — breaks feeds
]

def matches_any(patterns, text):
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def is_ai_related(text: str) -> bool:
    """Smart filter that allows real AI research but blocks junk."""
    if not text:
        return False

    text = text.lower()

    # ❌ Hard block junk / meta / hiring / promotion
    if matches_any(EXCLUDE_PATTERNS, text):
        return False

    # ✔ Allow AI based on context keywords (balanced)
    if matches_any(AI_KEYWORDS, text):
        return True

    # ✔ Catch implied AI content (e.g., embeddings, GPUs, models)
    context_terms = ["gpu", "tpu", "weights", "parameters", "architecture"]
    if any(ct in text for ct in context_terms):
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
# MAIN FETCHER
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
        print(f"📡 Source: {source.name}")

        try:
            response = requests.get(source.url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"⚠️ HTTP {response.status_code}")
                continue

            feed = feedparser.parse(response.content)

            if not feed.entries:
                print("⚠️ No entries")
                continue

            for entry in feed.entries[:20]:  # fetch more entries
                title = clean_html(getattr(entry, "title", ""))
                link = getattr(entry, "link", "")
                summary = clean_html(
                    getattr(entry, "summary", "") or 
                    getattr(entry, "description", "")
                )

                parts = [title, summary]

                # include full content if available
                if hasattr(entry, "content"):
                    for c in entry.content:
                        parts.append(clean_html(c.value))

                full_text = " ".join(parts).lower()

                # skip if not AI
                if not is_ai_related(full_text):
                    print(f"   ⏩ Skip: {title[:60]}")
                    continue

                # skip duplicates
                if crud.news_exists(db, link):
                    continue

                # SAVE
                item = crud.create_news_item(
                    db=db,
                    title=title,
                    summary=summary or title,
                    url=link,
                    source_id=source.id,
                    published_at=datetime.now()
                )

                if item:
                    print(f"   ✅ Saved: {title[:80]}")
                    new_count += 1

        except Exception as e:
            print(f"❌ Error in {source.name}: {e}")

    print(f"\n🏁 Done. Total saved: {new_count}\n")
    return new_count
