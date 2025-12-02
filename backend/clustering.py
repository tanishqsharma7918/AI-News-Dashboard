from sqlalchemy.orm import Session
from openai import OpenAI
import numpy as np
import models
import math
from datetime import datetime

# -------------------------------
# CONFIG
# -------------------------------
client = OpenAI()

EMBED_MODEL = "text-embedding-3-large"
SIMILARITY_THRESHOLD = 0.78     # strict for semantic relevance
MAX_RECENT_TOPICS = 30

# Strong AI keywords (to ensure only AI content is clustered)
AI_KEYWORDS = {
    "ai", "artificial intelligence", "machine learning", "ml",
    "deep learning", "neural", "neural network", "robotics",
    "vision model", "nlp", "transformer", "rag",
    "llm", "large language model", "chatgpt", "openai",
    "anthropic", "google ai", "meta ai"
}

# -------------------------------
# HELPERS
# -------------------------------

def contains_ai_keyword(text: str) -> bool:
    text = text.lower()
    return any(kw in text for kw in AI_KEYWORDS)


def embed_text(text: str) -> list:
    """Generate embedding for any text."""
    if not text or text.strip() == "":
        return None

    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )

    return response.data[0].embedding


def cosine_sim(a, b):
    """Cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def calculate_popularity(topic, article_count, unique_sources):
    coverage = min(article_count * 10, 100)
    diversity = min(unique_sources * 20, 100)
    velocity = 60  # static baseline
    return round((0.4 * coverage) + (0.2 * diversity) + (0.2 * velocity), 1)


def generate_topic_title(article_title, article_summary):
    """Creates clean, readable topic titles."""
    base = article_title.split(":")[0]
    if len(base) < 50:
        return base.strip()
    return (base[:60] + "...").strip()


# -------------------------------
# MAIN CLUSTERING
# -------------------------------

def run_clustering(db: Session):
    print("🧠 Running Semantic AI Topic Clustering...")

    # Fetch unclustered articles
    new_articles = db.query(models.NewsItem).filter(
        models.NewsItem.topic_id == None
    ).all()

    if not new_articles:
        print("   ✔ No new articles to cluster.")
        return

    # Preload recent topics (limit to reduce noise)
    existing_topics = db.query(models.Topic).order_by(
        models.Topic.created_at.desc()
    ).limit(MAX_RECENT_TOPICS).all()

    # Ensure all existing topic embeddings are loaded
    for topic in existing_topics:
        if not topic.embedding:
            topic_text = f"{topic.title}. {topic.summary}"
            topic.embedding = embed_text(topic_text)
            db.commit()

    for article in new_articles:

        # Combine text for embedding
        text = f"{article.title}. {article.summary}"

        # Skip non-AI articles
        if not contains_ai_keyword(text):
            print(f"   ❌ Skipping non-AI article: {article.title[:40]}")
            continue

        # Embed article
        article_embedding = embed_text(text)
        if not article_embedding:
            print(f"   ⚠ Skipping article (no embedding): {article.title}")
            continue

        best_topic = None
        best_sim = 0

        # -------------------------------
        # Find best matching topic
        # -------------------------------
        for topic in existing_topics:
            if not topic.embedding:
                continue

            sim = cosine_sim(article_embedding, topic.embedding)

            if sim > best_sim and sim >= SIMILARITY_THRESHOLD:
                best_sim = sim
                best_topic = topic

        # -------------------------------
        # Assign to existing topic
        # -------------------------------
        if best_topic:
            article.topic_id = best_topic.id

            print(f"   ↳ Added to Topic: {best_topic.title}   (sim={best_sim:.2f})")

            count = len(best_topic.articles)
            sources = len(set(a.source_id for a in best_topic.articles))
            best_topic.popularity_score = calculate_popularity(best_topic, count, sources)

            db.commit()
            continue

        # -------------------------------
        # Create new topic
        # -------------------------------
        new_topic_title = generate_topic_title(article.title, article.summary)

        new_topic = models.Topic(
            title=new_topic_title,
            summary=article.summary,
            embedding=article_embedding,
            popularity_score=10.0,
            created_at=datetime.utcnow()
        )

        db.add(new_topic)
        db.commit()

        article.topic_id = new_topic.id

        print(f"   ✨ New AI Topic: {new_topic.title}")

    db.commit()
    print("✔ Semantic clustering completed.")
