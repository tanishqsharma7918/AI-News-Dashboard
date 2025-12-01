from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
import crud
import fetcher
import clustering
import seed
from database import engine, get_db
from pydantic import BaseModel


class BroadcastRequest(BaseModel):
    news_id: int
    platform: str


# 1. Create Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 2. CORS (Frontend Access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3. AUTOMATION: Run on Startup
@app.on_event("startup")
def startup_event():
    # We need a new database session for this background task
    db = next(get_db())
    try:
        # Check if DB is empty
        existing_sources = db.query(models.Source).first()
        if not existing_sources:
            print("🚀 First run detected! Seeding database...")
            seed.seed_sources()  # Add the 20 sources
            fetcher.fetch_and_store_news(db)  # Fetch the first batch of news

            # --- CRITICAL FIX 1: RUN CLUSTERING ON STARTUP ---
            clustering.run_clustering(db)  # <<< ADDED THIS

            print("✅ Initialization & Clustering complete. News ready.")
        else:
            print("⚡ Database already initialized.")
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"status": "System Online", "database": "Connected"}


@app.get("/topics")
def get_popular_topics(db: Session = Depends(get_db)):
    topics = db.query(models.Topic).order_by(models.Topic.popularity_score.desc()).limit(20).all()

    # Transform data to include the URL of the first article
    response_data = []
    for t in topics:
        # Get the first article associated with this topic
        first_article = t.articles[0] if t.articles else None
        response_data.append({
            "id": t.id,
            "title": t.title,
            "summary": t.summary,
            "popularity_score": t.popularity_score,
            "url": first_article.url if first_article else "#"  # <--- NEW FIELD
        })

    return response_data


@app.get("/news")
def read_news(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return crud.get_news_items(db, skip=skip, limit=limit)


@app.post("/news/{news_id}/favorite")
def toggle_favorite(news_id: int, db: Session = Depends(get_db)):
    item = db.query(models.NewsItem).filter(models.NewsItem.id == news_id).first()
    if item:
        item.is_favorite = not item.is_favorite
        db.commit()
        return {"status": "success", "is_favorite": item.is_favorite}
    return {"error": "Item not found"}


@app.post("/fetch-news")
def trigger_fetch(db: Session = Depends(get_db)):
    count = fetcher.fetch_and_store_news(db)

    # --- CRITICAL FIX 2: RUN CLUSTERING ON MANUAL REFRESH ---
    clustering.run_clustering(db)  # <<< ADDED THIS

    return {"status": "success", "new_items_saved": count, "clustering": "completed"}


@app.post("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    return {"message": "Database is connected!"}


@app.post("/broadcast")
def broadcast_news(request: BroadcastRequest, db: Session = Depends(get_db)):
    print(f"📣 BROADCASTING News #{request.news_id} to {request.platform}...")
    return {"status": "success", "platform": request.platform, "message": "Broadcast Logged"}