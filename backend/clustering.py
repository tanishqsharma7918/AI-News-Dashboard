from sqlalchemy.orm import Session
from openai import OpenAI
import numpy as np
import models
import math
import re
from datetime import datetime

# -------------------------------
# CONFIG
# -------------------------------

client = OpenAI()

EMBED_MODEL = "text-embedding-3-large"
SIMILARITY_THRESHOLD = 0.70        # lower threshold to group more related articles together
MAX_RECENT_TOPICS = 30

# Strong AI-only detection
AI_KEYWORDS = {
    "ai", "artificial intelligence",
    "machine learning", "ml",
    "deep learning", "neural", "neural network",
    "robotics", "computer vision",
    "nlp", "transformer", "rag",
    "llm", "large language model",
    "chatgpt", "gpt", "openai",
    "anthropic", "meta ai", "google ai",
}

# Patterns to block Reddit/meta/hiring/non-news posts
NON_NEWS_PATTERNS = [
    "[d] self-promotion",
    "self-promotion thread",
    "who's hiring",
    "who wants to be hired",
    "monthly thread",
    "meta thread",
    "discussion thread",
    "automoderator",
    "reddit",
]


# -------------------------------
# FILTER HELPERS
# -------------------------------

def contains_ai_keyword(text: str) -> bool:
    """Matches AI keywords by full words only to prevent false positives."""
    text = text.lower()
    for kw in AI_KEYWORDS:
        if re.search(rf'\b{re.escape(kw)}\b', text):
            return True
    return False


def is_meta_or_non_ai_thread(text: str) -> bool:
    """Block Reddit/meta threads completely."""
    text = text.lower()
    return any(p in text for p in NON_NEWS_PATTERNS)


# -------------------------------
# EMBEDDING / MATH HELPERS
# -------------------------------

def embed_text(text: str) -> list:
    """Generate embedding for text."""
    if not text or text.strip() == "":
        return None
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=text,
    )
    return response.data[0].embedding


def cosine_sim(a, b):
    """Cosine similarity between vectors."""
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def calculate_popularity(topic, article_count, unique_sources):
    coverage = min(article_count * 10, 100)
    diversity = min(unique_sources * 20, 100)
    velocity = 60
    return round((0.4 * coverage) + (0.2 * diversity) + (0.2 * velocity), 1)


def generate_topic_title(title: str, summary: str) -> str:
    """Cleaner titles for new clusters."""
    title = title.strip()

    # Remove tags like [D], [Meta], etc.
    title = re.sub(r'^\[[^\]]+\]\s*', '', title)

    # If title is too generic, fallback to summary
    if len(title) < 5:
        return summary[:80] + "..."

    # Truncate long titles
    if len(title) > 80:
        title = title[:80] + "..."

    return title


# -------------------------------
# MAIN CLUSTERING LOGIC
# -------------------------------

def run_clustering(db: Session):
    print("🧠 Running Semantic AI Topic Clustering...")

    new_articles = db.query(models.NewsItem).filter(
        models.NewsItem.topic_id == None
    ).all()

    if not new_articles:
        print("✔ No new articles to cluster.")
        return

    # Preload recent topics
    existing_topics = db.query(models.Topic).order_by(
        models.Topic.created_at.desc()
    ).limit(MAX_RECENT_TOPICS).all()

    # Ensure all topic embeddings exist
    for topic in existing_topics:
        if not topic.embedding:
            topic_text = f"{topic.title}. {topic.summary}"
            topic.embedding = embed_text(topic_text)
            db.commit()

    # -------------------------------
    # PROCESS EACH NEW ARTICLE
    # -------------------------------
    for article in new_articles:

        text = f"{article.title}. {article.summary}".strip().lower()

        # 🚫 Block Reddit/meta/hiring/noise posts
        if is_meta_or_non_ai_thread(text):
            print(f"   ❌ Skipped META/Reddit Thread: {article.title[:60]}")
            continue

        # 🚫 Skip non-AI articles early
        if not contains_ai_keyword(text):
            print(f"   ❌ Non-AI Article Skipped: {article.title[:60]}")
            continue

        # Generate article embedding
        article_embedding = embed_text(f"{article.title}. {article.summary}")
        if not article_embedding:
            print(f"⚠ No embedding for article: {article.title}")
            continue

        best_topic = None
        best_sim = 0

        # ----------------------------------------
        # Match to existing topic if similarity > threshold
        # ----------------------------------------
        for topic in existing_topics:
            if not topic.embedding:
                continue

            sim = cosine_sim(article_embedding, topic.embedding)

            if sim > best_sim and sim >= SIMILARITY_THRESHOLD:
                best_sim = sim
                best_topic = topic

        # ----------------------------------------
        # Assign to existing topic
        # ----------------------------------------
        if best_topic:
            article.topic_id = best_topic.id
            db.commit()
            db.refresh(best_topic)

            print(f"   ↳ Added to Topic: {best_topic.title}  (sim={best_sim:.2f})")

            # Update topic popularity
            count = len(best_topic.articles)
            sources = len(set(a.source_id for a in best_topic.articles))
            best_topic.popularity_score = calculate_popularity(best_topic, count, sources)

            db.commit()
            continue

        # ----------------------------------------
        # Create NEW topic
        # ----------------------------------------
        new_title = generate_topic_title(article.title, article.summary)

        new_topic = models.Topic(
            title=new_title,
            summary=article.summary,
            embedding=article_embedding,
            popularity_score=10.0,
            created_at=datetime.utcnow()
        )

        db.add(new_topic)
        db.commit()
        db.refresh(new_topic)

        article.topic_id = new_topic.id
        db.commit()

        print(f"   ✨ New AI Topic Created: {new_title}")

    print("✔ Semantic clustering complete.")
