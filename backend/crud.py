from sqlalchemy.orm import Session
import models

def get_active_sources(db: Session):
    return db.query(models.Source).filter(models.Source.active == True).all()

def get_news_by_url(db: Session, url: str):
    return db.query(models.NewsItem).filter(models.NewsItem.url == url).first()

def create_news_item(db: Session, title: str, summary: str, url: str, source_id: int, published_at=None):
    if get_news_by_url(db, url):
        return None  # Skip duplicate

    new_item = models.NewsItem(
        title=title,
        summary=summary,
        url=url,
        source_id=source_id,
        published_at=published_at
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

# --- THIS WAS MISSING ---
# Updated function to fetch Source Name
def get_news_items(db: Session, skip: int = 0, limit: int = 50):
    # Query both NewsItem AND Source tables
    results = db.query(models.NewsItem, models.Source) \
        .join(models.Source, models.NewsItem.source_id == models.Source.id) \
        .order_by(models.NewsItem.published_at.desc()) \
        .offset(skip) \
        .limit(limit) \
        .all()

    # Convert to a clean list of dictionaries
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
            "source_name": source.name  # <--- THIS IS THE NEW MAGIC FIELD
        })

    return news_list