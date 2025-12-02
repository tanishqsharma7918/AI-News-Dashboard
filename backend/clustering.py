from sqlalchemy.orm import Session
import models
import math
from difflib import SequenceMatcher

# Strong AI keywords for filtering and clustering
AI_KEYWORDS = {
    "ai", "artificial intelligence", "machine learning", "ml", "deep learning",
    "chatgpt", "gpt", "openai", "google ai", "meta ai", "llm",
    "neural", "transformer", "rag", "nlp", "vision model",
    "robot", "robotics", "autonomous", "automation"
}

def title_similarity(a: str, b: str) -> float:
    """A simple ratio-based similarity for fallback."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def contains_ai_keyword(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in AI_KEYWORDS)


def calculate_popularity(topic, article_count, unique_sources):
    coverage = min(article_count * 10, 100)
    diversity = min(unique_sources * 20, 100)
    velocity = 50
    return round((0.4 * coverage) + (0.2 * diversity) + (0.2 * velocity), 1)


def run_clustering(db: Session):
    print("🧠 Running AI Topic Clustering...")

    # Fetch ALL unclustered news but only AI-related
    recent_news = db.query(models.NewsItem).filter(
        models.NewsItem.topic_id == None
    ).all()

    for article in recent_news:

        # ❌ Skip NON-AI articles entirely
        if not contains_ai_keyword(article.title + " " + article.summary):
            print(f"   ❌ Skipping non-AI article: {article.title[:40]}")
            continue

        found_topic = False

        # Look at recent topics only
        existing_topics = db.query(models.Topic).order_by(
            models.Topic.created_at.desc()
        ).limit(25).all()

        for topic in existing_topics:

            # Skip topics that are not AI-related
            if not contains_ai_keyword(topic.title + " " + topic.summary):
                continue

            # Basic keyword intersection
            topic_words = set(topic.title.lower().split())
            article_words = set(article.title.lower().split())
            keyword_overlap = len(topic_words.intersection(article_words))

            # Fallback: Title similarity score
            sim = title_similarity(article.title, topic.title)

            if keyword_overlap >= 2 or sim >= 0.30:
                article.topic_id = topic.id
                found_topic = True

                print(f"   ↳ Added to Topic: {topic.title}")

                # Update topic popularity score
                count = len(topic.articles)
                sources = len(set(a.source_id for a in topic.articles))
                topic.popularity_score = calculate_popularity(topic, count, sources)

                break

        # Create NEW Topic
        if not found_topic:
            new_topic = models.Topic(
                title=article.title,
                summary=article.summary,
                popularity_score=10.0
            )
            db.add(new_topic)
            db.commit()

            article.topic_id = new_topic.id

            print(f"   ✨ New AI Topic: {new_topic.title}")

    db.commit()
