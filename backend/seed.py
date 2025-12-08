from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

# List of 40+ Top AI/ML/GenAI Sources (RSS Feeds)
SOURCES = [
    # Major Tech Companies - AI Labs
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "type": "rss"},
    {"name": "Google AI Blog", "url": "http://googleaiblog.blogspot.com/atom.xml", "type": "rss"},
    {"name": "DeepMind", "url": "https://deepmind.google/blog/rss.xml", "type": "rss"},
    {"name": "Meta AI", "url": "https://ai.meta.com/blog/rss.xml", "type": "rss"},
    {"name": "Microsoft AI", "url": "https://blogs.microsoft.com/ai/feed/", "type": "rss"},
    {"name": "Apple Machine Learning", "url": "https://machinelearning.apple.com/rss.xml", "type": "rss"},
    {"name": "NVIDIA AI Blog", "url": "https://blogs.nvidia.com/feed/", "type": "rss"},
    {"name": "AWS Machine Learning", "url": "https://aws.amazon.com/blogs/machine-learning/feed/", "type": "rss"},
    
    # AI Research & Academia
    {"name": "ArXiv (CS - AI)", "url": "http://export.arxiv.org/rss/cs.AI", "type": "rss"},
    {"name": "ArXiv (CS - LG)", "url": "http://export.arxiv.org/rss/cs.LG", "type": "rss"},
    {"name": "Berkeley AI Research", "url": "https://bair.berkeley.edu/blog/feed.xml", "type": "rss"},
    {"name": "Stanford AI Lab", "url": "https://ai.stanford.edu/blog/feed.xml", "type": "rss"},
    {"name": "MIT CSAIL", "url": "https://www.csail.mit.edu/rss.xml", "type": "rss"},
    
    # AI News & Media
    {"name": "MIT Technology Review (AI)", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/", "type": "rss"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/", "type": "rss"},
    {"name": "The Verge (AI)", "url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml", "type": "rss"},
    {"name": "Wired (AI)", "url": "https://www.wired.com/feed/tag/ai/latest/rss", "type": "rss"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "type": "rss"},
    {"name": "The Information AI", "url": "https://www.theinformation.com/articles/ai/feed", "type": "rss"},
    
    # AI Platforms & Tools
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml", "type": "rss"},
    {"name": "Anthropic Blog", "url": "https://www.anthropic.com/blog/rss.xml", "type": "rss"},
    {"name": "Cohere Blog", "url": "https://cohere.com/blog/feed", "type": "rss"},
    {"name": "Replicate Blog", "url": "https://replicate.com/blog/feed", "type": "rss"},
    
    # ML Engineering & Tutorials
    {"name": "Towards Data Science", "url": "https://towardsdatascience.com/feed", "type": "rss"},
    {"name": "Machine Learning Mastery", "url": "https://machinelearningmastery.com/feed/", "type": "rss"},
    {"name": "KDnuggets", "url": "https://www.kdnuggets.com/feed", "type": "rss"},
    {"name": "Analytics Vidhya", "url": "https://www.analyticsvidhya.com/feed/", "type": "rss"},
    {"name": "MarkTechPost", "url": "https://www.marktechpost.com/feed/", "type": "rss"},
    
    # Community & Discussion
    {"name": "Reddit Machine Learning", "url": "https://www.reddit.com/r/MachineLearning/.rss", "type": "rss"},
    {"name": "Reddit Artificial", "url": "https://www.reddit.com/r/artificial/.rss", "type": "rss"},
    {"name": "Reddit LocalLLaMA", "url": "https://www.reddit.com/r/LocalLLaMA/.rss", "type": "rss"},
    
    # AI Startups & Products
    {"name": "AI Alignment Forum", "url": "https://www.alignmentforum.org/feed.xml", "type": "rss"},
    {"name": "LessWrong AI", "url": "https://www.lesswrong.com/feed.xml", "type": "rss"},
    {"name": "Import AI", "url": "https://jack-clark.net/feed/", "type": "rss"},
    
    # Industry Specific
    {"name": "Google Cloud AI", "url": "https://cloud.google.com/blog/products/ai-machine-learning/rss", "type": "rss"},
    {"name": "Azure AI Blog", "url": "https://azure.microsoft.com/en-us/blog/tag/azure-ai/feed/", "type": "rss"},
    
    # Generative AI Focused
    {"name": "Stability AI Blog", "url": "https://stability.ai/news/rss", "type": "rss"},
    {"name": "Midjourney Updates", "url": "https://www.midjourney.com/feed", "type": "rss"},
    
    # AI Ethics & Policy
    {"name": "AI Now Institute", "url": "https://ainowinstitute.org/feed", "type": "rss"},
    {"name": "Partnership on AI", "url": "https://www.partnershiponai.org/feed/", "type": "rss"},
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
