from sqlalchemy.orm import Session
import models
from models import NewsItem, Source


# ============================================================
# SOURCES
# ============================================================

def get_active_sources(db: Session):
    """Return list of active RSS/AI sources."""
    return db.query(Source).filter(Source.active == True).all()


# ============================================================
# NEWS ITEM HELPERS
# ============================================================

def get_news_by_url(db: Session, url: str):
    """Return a news item if URL exists."""
    return db.query(NewsItem).filter(NewsItem.url == url).first()


def news_exists(db: Session, url: str) -> bool:
    """Simple exists() wrapper used by fetcher."""
    return db.query(NewsItem).filter(NewsItem.url == url).first() is not None


def create_news_item(db: Session, title: str, summary: str, url: str, source_id: int, published_at=None):
    """Create a new news row unless already exists."""
    if news_exists(db, url):
        return None  # Duplicate — skip

    item = NewsItem(
        title=title,
        summary=summary,
        url=url,
        source_id=source_id,
        published_at=published_at
    )

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# ============================================================
# FETCH PAGINATED NEWS INCLUDING SOURCE NAME
# ============================================================

def get_news_items(db: Session, skip: int = 0, limit: int = 50):
    """
    Returns a list of the newest news items joined with their source name.
    """
    results = (
        db.query(NewsItem, Source)
        .join(Source, NewsItem.source_id == Source.id)
        .order_by(NewsItem.published_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    news_list = []
    for item, source in results:
        news_list.append({
            "id": item.id,
            "title": item.title,
            "summary": item.summary,
            "url": item.url,
            "source_id": item.source_id,
            "published_at": item.published_at,
            "is_favorite": item.is_favorite,
            "source_name": source.name,
        })

    return news_list
