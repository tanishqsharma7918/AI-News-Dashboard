#!/usr/bin/env python3
"""
Quick database statistics viewer
Run in Render Shell: python3 show_stats.py
"""

from database import SessionLocal
import models
from datetime import datetime, timedelta

def main():
    db = SessionLocal()
    try:
        # Basic counts
        total_articles = db.query(models.NewsItem).count()
        total_topics = db.query(models.Topic).count()
        linked_articles = db.query(models.NewsItem).filter(
            models.NewsItem.topic_id != None
        ).count()
        unlinked_articles = db.query(models.NewsItem).filter(
            models.NewsItem.topic_id == None
        ).count()
        active_sources = db.query(models.Source).filter(
            models.Source.active == True
        ).count()
        
        print("\n" + "=" * 60)
        print("📊 AI NEWS DASHBOARD - DATABASE STATISTICS")
        print("=" * 60)
        
        print("\n📰 ARTICLES:")
        print(f"   Total:              {total_articles}")
        print(f"   Linked to topics:   {linked_articles}")
        print(f"   Unlinked:           {unlinked_articles}")
        
        print("\n📁 TOPICS:")
        print(f"   Total topics:       {total_topics}")
        if total_topics > 0 and linked_articles > 0:
            avg = linked_articles / total_topics
            print(f"   Avg articles/topic: {avg:.1f}")
            
            # Quality indicator
            if avg < 2:
                print(f"   Status: ⚠️  Too granular (threshold too high)")
            elif avg > 10:
                print(f"   Status: ⚠️  Too broad (threshold too low)")
            else:
                print(f"   Status: ✅ Healthy clustering")
        
        print("\n📡 SOURCES:")
        print(f"   Active sources:     {active_sources}")
        
        # Recent articles
        recent = db.query(models.NewsItem).order_by(
            models.NewsItem.created_at.desc()
        ).limit(5).all()
        
        if recent:
            print("\n📅 LATEST 5 ARTICLES:")
            for i, article in enumerate(recent, 1):
                source = db.query(models.Source).filter_by(id=article.source_id).first()
                source_name = source.name if source else "Unknown"
                title_short = article.title[:50] + "..." if len(article.title) > 50 else article.title
                print(f"   {i}. [{source_name}] {title_short}")
        
        # Articles by source (top 10)
        print("\n📊 TOP 10 SOURCES BY ARTICLE COUNT:")
        sources = db.query(models.Source).filter_by(active=True).all()
        source_counts = []
        for source in sources:
            count = db.query(models.NewsItem).filter_by(source_id=source.id).count()
            source_counts.append((source.name, count))
        
        source_counts.sort(key=lambda x: x[1], reverse=True)
        for i, (name, count) in enumerate(source_counts[:10], 1):
            print(f"   {i:2}. {name:30} {count:3} articles")
        
        # Topics with most articles
        if total_topics > 0:
            print("\n🔥 TOP 5 MOST POPULAR TOPICS:")
            topics = db.query(models.Topic).order_by(
                models.Topic.popularity_score.desc()
            ).limit(5).all()
            
            for i, topic in enumerate(topics, 1):
                article_count = db.query(models.NewsItem).filter_by(
                    topic_id=topic.id
                ).count()
                title_short = topic.title[:45] + "..." if len(topic.title) > 45 else topic.title
                print(f"   {i}. [{article_count} articles] {title_short}")
        
        print("\n" + "=" * 60)
        print("✅ Statistics generated successfully!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
