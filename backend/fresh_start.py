#!/usr/bin/env python3
"""
COMPLETE FRESH START - Delete everything and reload
- Deletes ALL articles and topics
- Fetches fresh articles from all 40 sources
- Re-clusters with 0.65 threshold
Run in Render Shell: python3 fresh_start.py
"""

from database import SessionLocal
import models
import fetcher
import clustering
import sys

def main():
    print("=" * 70)
    print("🔄 COMPLETE FRESH START - DELETING ALL DATA")
    print("=" * 70)
    print("\n⚠️  WARNING: This will delete ALL articles and topics!")
    print("   A fresh dataset will be fetched from all 40 sources.\n")
    
    db = SessionLocal()
    try:
        # Step 1: Show current state
        current_articles = db.query(models.NewsItem).count()
        current_topics = db.query(models.Topic).count()
        active_sources = db.query(models.Source).filter_by(active=True).count()
        
        print(f"📊 Current Database:")
        print(f"   Articles: {current_articles}")
        print(f"   Topics: {current_topics}")
        print(f"   Active sources: {active_sources}")
        
        # Step 2: Clear topic assignments first (to avoid foreign key errors)
        print(f"\n🗑️  Step 1: Clearing topic assignments...")
        db.query(models.NewsItem).update({"topic_id": None})
        db.commit()
        print(f"   ✓ Cleared all topic assignments")
        
        # Step 3: Delete all topics
        print(f"\n🗑️  Step 2: Deleting all topics...")
        deleted_topics = db.query(models.Topic).delete()
        db.commit()
        print(f"   ✓ Deleted {deleted_topics} topics")
        
        # Step 4: Delete all articles
        print(f"\n🗑️  Step 3: Deleting all articles...")
        deleted_articles = db.query(models.NewsItem).delete()
        db.commit()
        print(f"   ✓ Deleted {deleted_articles} articles")
        
        # Step 5: Fetch fresh articles
        print(f"\n📰 Step 4: Fetching fresh articles from {active_sources} sources...")
        print(f"   ⏳ This will take 3-5 minutes...")
        print(f"   Fetching from all RSS feeds...\n")
        
        try:
            new_articles = fetcher.fetch_and_store_news(db)
            print(f"\n   ✅ Fetched {new_articles} fresh articles!")
        except Exception as e:
            print(f"\n   ⚠️  Fetch completed with some errors: {e}")
            new_articles = db.query(models.NewsItem).count()
            print(f"   Articles in database: {new_articles}")
        
        # Step 6: Run clustering
        total_articles = db.query(models.NewsItem).count()
        
        if total_articles == 0:
            print(f"\n❌ No articles fetched. Please check your internet connection and RSS feeds.")
            sys.exit(1)
        
        print(f"\n🧠 Step 5: Clustering {total_articles} articles...")
        print(f"   Threshold: {clustering.SIMILARITY_THRESHOLD}")
        print(f"   Model: {clustering.EMBED_MODEL}")
        print(f"   ⏳ This will take 2-3 minutes...\n")
        
        try:
            clustering.run_clustering(db)
        except Exception as e:
            print(f"\n   ⚠️  Clustering error (continuing): {e}")
        
        # Step 7: Final statistics
        final_articles = db.query(models.NewsItem).count()
        final_topics = db.query(models.Topic).count()
        linked = db.query(models.NewsItem).filter(
            models.NewsItem.topic_id != None
        ).count()
        unlinked = db.query(models.NewsItem).filter(
            models.NewsItem.topic_id == None
        ).count()
        
        print(f"\n" + "=" * 70)
        print(f"✅ FRESH START COMPLETE!")
        print(f"=" * 70)
        print(f"\n📊 NEW DATABASE STATE:")
        print(f"   Total articles:       {final_articles}")
        print(f"   Articles linked:      {linked}")
        print(f"   Articles unlinked:    {unlinked} (non-AI content)")
        print(f"   Topics created:       {final_topics}")
        
        if final_topics > 0 and linked > 0:
            ratio = linked / final_topics
            print(f"   Avg per topic:        {ratio:.1f}")
            
            if ratio >= 3 and ratio <= 10:
                print(f"\n   ✅ Excellent! Healthy clustering.")
            elif ratio < 3:
                print(f"\n   ⚠️  A bit granular, but okay.")
            else:
                print(f"\n   ⚠️  Topics might be too broad.")
        
        # Show top 15 topics
        print(f"\n🔥 TOP 15 POPULAR TOPICS:")
        top_topics = db.query(models.Topic).order_by(
            models.Topic.popularity_score.desc()
        ).limit(15).all()
        
        for i, topic in enumerate(top_topics, 1):
            article_count = db.query(models.NewsItem).filter_by(
                topic_id=topic.id
            ).count()
            
            # Get the first article title for display
            first_article = db.query(models.NewsItem).filter_by(
                topic_id=topic.id
            ).order_by(models.NewsItem.published_at.desc()).first()
            
            if first_article:
                title = first_article.title
                title_short = title[:55] + "..." if len(title) > 55 else title
            else:
                title_short = topic.title[:55] + "..." if len(topic.title) > 55 else topic.title
            
            print(f"   {i:2}. [{article_count} articles] {title_short}")
        
        # Show source statistics
        print(f"\n📊 TOP 10 SOURCES BY ARTICLE COUNT:")
        sources = db.query(models.Source).filter_by(active=True).all()
        source_counts = []
        
        for source in sources:
            count = db.query(models.NewsItem).filter_by(source_id=source.id).count()
            if count > 0:
                source_counts.append((source.name, count))
        
        source_counts.sort(key=lambda x: x[1], reverse=True)
        
        for i, (name, count) in enumerate(source_counts[:10], 1):
            print(f"   {i:2}. {name:35} {count:3} articles")
        
        print(f"\n" + "=" * 70)
        print(f"🌐 Your dashboard is ready!")
        print(f"   Frontend: https://ai-news-frontend-d1ld.onrender.com")
        print(f"   Backend:  https://ai-news-backend-age8.onrender.com")
        print(f"=" * 70)
        print(f"\n✅ All done! Fresh articles loaded and clustered.\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
