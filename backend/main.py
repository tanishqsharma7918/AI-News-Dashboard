from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from fastapi import HTTPException

import models
import crud
import fetcher
import clustering
import seed

from database import engine, get_db


# ------------------------------------------------------
# SCHEMAS
# ------------------------------------------------------
class BroadcastRequest(BaseModel):
    news_id: int
    platform: str


# ------------------------------------------------------
# INITIAL SETUP
# ------------------------------------------------------
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI News Dashboard Backend", version="2.0")


# ------------------------------------------------------
# CORS (Frontend)
# ------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # allow all domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------
# APP STARTUP BOOTSTRAP
# ------------------------------------------------------
@app.on_event("startup")
def startup_event():
    db = next(get_db())
    try:
        existing_sources = db.query(models.Source).first()

        if not existing_sources:
            print("🚀 First Run Detected → Seeding Sources…")
            seed.seed_sources()

            print("🌐 Fetching initial AI news…")
            fetcher.fetch_and_store_news(db)

            print("🧠 Running Initial Semantic Clustering…")
            clustering.run_clustering(db)

            print("✅ System Ready!")
        else:
            print("⚡ Backend Ready — DB Already Initialized.")
    finally:
        db.close()


# ------------------------------------------------------
# ROOT CHECK
# ------------------------------------------------------
@app.get("/")
def read_root():
    return {"status": "online", "message": "AI News Dashboard Backend Running"}


# ------------------------------------------------------
# GET TOPICS (MAIN ENDPOINT FOR FRONTEND)
# ------------------------------------------------------
@app.get("/topics")
def get_topics(db: Session = Depends(get_db)):
    topics = (
        db.query(models.Topic)
        .options(joinedload(models.Topic.articles))
        .order_by(models.Topic.popularity_score.desc())
        .limit(25)
        .all()
    )

    response = []
    for topic in topics:
        articles = [
            {
                "id": a.id,
                "title": a.title,
                "url": a.url,
                "source_id": a.source_id,
                "published_at": a.published_at,
            }
            for a in topic.articles
        ]

        first_url = articles[0]["url"] if articles else "#"

        response.append({
            "id": topic.id,
            "title": topic.title,
            "summary": topic.summary,
            "popularity_score": topic.popularity_score,
            "url": first_url,
            "articles": articles,
        })

    return response


# ------------------------------------------------------
# GET RAW NEWS (OPTIONAL)
# ------------------------------------------------------
@app.get("/news")
def read_news(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return crud.get_news_items(db, skip=skip, limit=limit)


# ------------------------------------------------------
# MARK NEWS AS FAVORITE
# ------------------------------------------------------
@app.post("/news/{news_id}/favorite")
def toggle_favorite(news_id: int, db: Session = Depends(get_db)):
    item = db.query(models.NewsItem).filter(models.NewsItem.id == news_id).first()
    if not item:
        return {"error": "News item not found"}

    item.is_favorite = not item.is_favorite
    db.commit()

    return {"status": "success", "is_favorite": item.is_favorite}


# ------------------------------------------------------
# FETCH NEW NEWS + RECLUSTER (MANUAL REFRESH)
# ------------------------------------------------------
@app.post("/fetch-news")
def trigger_fetch(db: Session = Depends(get_db)):
    try:
        print("\n⚡ Running News Fetcher...\n")
        inserted = fetcher.fetch_and_store_news(db)
        print(f"📰 Saved {inserted} new articles.")

        print("\n🧠 Running Semantic AI Topic Clustering...")
        topics_created = clustering.run_clustering(db)
        print(f"📌 Created {topics_created} new topics.")

        return {
            "status": "ok",
            "new_items_saved": inserted,
            "topics_created": topics_created
        }

    except Exception as e:
        print("❌ Fetch/Cluster Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------
# FORCE RE-CLUSTER ALL ARTICLES (FIX DATABASE)
# ------------------------------------------------------
@app.post("/reset-clustering")
def reset_clustering(db: Session = Depends(get_db)):
    try:
        print("\n🔄 Resetting all topic assignments...")
        
        # Clear all topic_id assignments
        db.query(models.NewsItem).update({"topic_id": None})
        db.commit()
        print("✔ Cleared all article-topic links")
        
        # Delete all existing topics
        deleted = db.query(models.Topic).delete()
        db.commit()
        print(f"✔ Deleted {deleted} old topics")
        
        # Re-run clustering
        print("\n🧠 Running fresh clustering...")
        clustering.run_clustering(db)
        
        # Count results
        total_topics = db.query(models.Topic).count()
        linked_articles = db.query(models.NewsItem).filter(models.NewsItem.topic_id != None).count()
        total_articles = db.query(models.NewsItem).count()
        
        return {
            "status": "success",
            "message": "Database reset and re-clustered",
            "topics_created": total_topics,
            "articles_linked": linked_articles,
            "total_articles": total_articles
        }
    except Exception as e:
        print(f"❌ Reset Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------------------------------
# TEST DB
# ------------------------------------------------------
@app.post("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    return {"message": "Database connection successful!"}


# ------------------------------------------------------
# BROADCAST (DUMMY ENDPOINT)
# ------------------------------------------------------
@app.post("/broadcast")
def broadcast_news(request: BroadcastRequest, db: Session = Depends(get_db)):
    print(f"📣 Sending News {request.news_id} → Platform: {request.platform}")
    return {"status": "success", "message": "Broadcast recorded"}
