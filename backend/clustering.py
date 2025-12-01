from sqlalchemy.orm import Session
import models
from datetime import datetime, timedelta
import math


def calculate_popularity(topic, article_count, unique_sources):
    # BRD Formula:
    # 0.4(Coverage) + 0.2(Diversity) + 0.2(Velocity) + 0.1(Social) + 0.1(Authority)

    coverage = min(article_count * 10, 100)  # Cap at 100
    diversity = min(unique_sources * 20, 100)  # 5 sources = 100 score
    velocity = 50  # Mocked for MVP (assumes steady flow)

    score = (0.4 * coverage) + (0.2 * diversity) + (0.2 * velocity)
    return round(score, 1)


def run_clustering(db: Session):
    print("🧠 Running Topic Clustering...")

    # 1. Get recent ungrouped news
    recent_news = db.query(models.NewsItem).filter(
        models.NewsItem.topic_id == None
    ).all()

    for article in recent_news:
        # Simple Clustering Logic:
        # Check if title matches an existing recent topic by > 60% similarity
        # (In production, use Embeddings/Vectors here)

        found_topic = False
        existing_topics = db.query(models.Topic).order_by(models.Topic.created_at.desc()).limit(20).all()

        for topic in existing_topics:
            # Basic keyword overlap check
            topic_words = set(topic.title.lower().split())
            article_words = set(article.title.lower().split())
            overlap = len(topic_words.intersection(article_words))

            if overlap >= 2:  # If 2+ major words match, group them
                article.topic_id = topic.id
                found_topic = True
                print(f"   ↳ Added '{article.title[:20]}...' to Topic: {topic.title}")

                # Update Topic Score
                count = len(topic.articles)
                sources = len(set([a.source_id for a in topic.articles]))
                topic.popularity_score = calculate_popularity(topic, count, sources)
                break

        if not found_topic:
            # Create NEW Topic
            new_topic = models.Topic(
                title=article.title,  # Use first article title as topic name
                summary=article.summary,
                popularity_score=10.0  # Starting score
            )
            db.add(new_topic)
            db.commit()
            article.topic_id = new_topic.id
            print(f"   ✨ Created New Topic: {new_topic.title}")

    db.commit()