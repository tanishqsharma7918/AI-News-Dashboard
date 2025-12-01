import feedparser
import requests
from sqlalchemy.orm import Session
import crud
from datetime import datetime


def fetch_and_store_news(db: Session):
    sources = crud.get_active_sources(db)
    new_count = 0

    print(f"🔄 Starting fetch for {len(sources)} sources...")

    # A strong "Browser Signature" to bypass blocks
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, application/atom+xml, text/xml, */*',
        'Connection': 'keep-alive'
    }

    for source in sources:
        print(f"📡 Fetching: {source.name}...")

        try:
            # STEP 1: Download raw content using Requests (Handles SSL & Headers better)
            response = requests.get(source.url, headers=HEADERS, timeout=10)

            if response.status_code != 200:
                print(f"   ⚠️ Blocked/Error: {source.name} (Status: {response.status_code})")
                continue

            # STEP 2: Parse the downloaded content
            feed = feedparser.parse(response.content)

            if not feed.entries:
                print(f"   ⚠️ Parsed but empty: {source.name}")
                continue

            # STEP 3: Process entries
            for entry in feed.entries[:5]:
                title = entry.title
                url = entry.link

                # Smart summary extraction
                summary = "No summary available."
                if hasattr(entry, 'summary'):
                    summary = entry.summary
                elif hasattr(entry, 'description'):
                    summary = entry.description

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
                    print(f"   ✅ Saved: {title[:30]}...")

        except Exception as e:
            print(f"   ❌ Critical Error {source.name}: {e}")

    print(f"🏁 Fetch complete. Total new items: {new_count}")
    return new_count