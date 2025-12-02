from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

# List of 20+ Top AI Sources (RSS Feeds)
SOURCES = [
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "type": "rss"},
    {"name": "MIT Technology Review (AI)",
     "url": "https://www.technologyreview.com/feed/topic/artificial-intelligence/", "type": "rss"},
    {"name": "Google AI Blog", "url": "http://googleaiblog.blogspot.com/atom.xml", "type": "rss"},
    {"name": "NVIDIA AI Blog", "url": "https://blogs.nvidia.com/feed/", "type": "rss"},
    {"name": "Microsoft AI", "url": "https://blogs.microsoft.com/ai/feed/", "type": "rss"},
    {"name": "AWS Machine Learning", "url": "https://aws.amazon.com/blogs/machine-learning/feed/", "type": "rss"},
    {"name": "Meta AI", "url": "https://ai.facebook.com/blog/rss", "type": "rss"},
    {"name": "KDnuggets", "url": "https://www.kdnuggets.com/feed", "type": "rss"},
    {"name": "MarkTechPost", "url": "https://www.marktechpost.com/feed/", "type": "rss"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/", "type": "rss"},
    {"name": "The Verge (AI)", "url": "https://www.theverge.com/rss/artificial-intelligence/index.xml", "type": "rss"},
    {"name": "Wired (AI)", "url": "https://www.wired.com/feed/tag/ai/latest/rss", "type": "rss"},
    {"name": "Towards Data Science", "url": "https://towardsdatascience.com/feed", "type": "rss"},
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml", "type": "rss"},
    {"name": "ArXiv (CS - AI)", "url": "http://export.arxiv.org/rss/cs.AI", "type": "rss"},
    {"name": "DeepMind", "url": "https://deepmind.google/blog/rss.xml", "type": "rss"},
    {"name": "Reddit Machine Learning", "url": "https://www.reddit.com/r/MachineLearning/.rss", "type": "rss"},
    {"name": "Berkeley AI Research", "url": "https://bair.berkeley.edu/blog/feed.xml", "type": "rss"},
    {"name": "Apple Machine Learning", "url": "https://machinelearning.apple.com/rss.xml", "type": "rss"},
]


def seed_sources():
    db = SessionLocal()
    print("🌱 Seeding Database with Sources...")
    try:
        added_count = 0
        for src in SOURCES:
            exists = db.query(models.Source).filter(models.Source.url == src["url"]).first()
            if not exists:
                new_source = models.Source(name=src["name"], url=src["url"], type=src["type"])
                db.add(new_source)
                added_count += 1
                print(f"   ✅ Added: {src['name']}")
            else:
                print(f"   ⚠️ Exists: {src['name']}")

        db.commit()
        print(f"\n🎉 Finished! Added {added_count} new sources.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_sources()

def get_news_items(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.NewsItem)\
             .order_by(models.NewsItem.published_at.desc())\
             .offset(skip)\
             .limit(limit)\
             .all()
