#!/usr/bin/env python3
"""
Quick re-cluster without cleanup (articles already cleaned)
Run in Render Shell: python3 quick_recluster.py
"""

from database import SessionLocal
import models
import clustering

def main():
    print("=" * 60)
    print("🧠 QUICK RE-CLUSTERING")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Show config
        print(f"\n📋 Configuration:")
        print(f"   Threshold: {clustering.SIMILARITY_THRESHOLD}")
        print(f"   Model: {clustering.EMBED_MODEL}")
        
        # Get counts
        total_articles = db.query(models.NewsItem).count()
        existing_topics = db.query(models.Topic).count()
        
        print(f"\n📊 Current State:")
        print(f"   Articles: {total_articles}")
        print(f"   Topics: {existing_topics}")
        
        # Reset
        print(f"\n🔄 Resetting clustering...")
        db.query(models.NewsItem).update({"topic_id": None})
        db.commit()
        
        deleted = db.query(models.Topic).delete()
        db.commit()
        print(f"   ✓ Deleted {deleted} topics")
        
        # Re-cluster
        print(f"\n🧠 Re-clustering with threshold {clustering.SIMILARITY_THRESHOLD}...")
        print(f"   ⏳ This may take 1-2 minutes...")
        
        clustering.run_clustering(db)
        
        # Results
        final_topics = db.query(models.Topic).count()
        linked = db.query(models.NewsItem).filter(models.NewsItem.topic_id != None).count()
        unlinked = db.query(models.NewsItem).filter(models.NewsItem.topic_id == None).count()
        
        print(f"\n" + "=" * 60)
        print(f"📊 RESULTS:")
        print(f"=" * 60)
        print(f"   Topics created:     {final_topics}")
        print(f"   Articles linked:    {linked}")
        print(f"   Articles unlinked:  {unlinked}")
        
        if final_topics > 0 and linked > 0:
            ratio = linked / final_topics
            print(f"   Avg per topic:      {ratio:.1f}")
            
            # Status
            if ratio < 2:
                print(f"\n   ⚠️  Still too granular")
                print(f"   💡 Try: threshold = 0.68")
            elif ratio > 10:
                print(f"\n   ⚠️  Too broad")
                print(f"   💡 Try: threshold = 0.75")
            else:
                print(f"\n   ✅ GOOD! Healthy clustering")
        
        # Show samples
        print(f"\n🔥 Top 15 Topics:")
        top = db.query(models.Topic).order_by(
            models.Topic.popularity_score.desc()
        ).limit(15).all()
        
        for i, topic in enumerate(top, 1):
            count = db.query(models.NewsItem).filter_by(topic_id=topic.id).count()
            title = topic.title[:52] + "..." if len(topic.title) > 52 else topic.title
            print(f"   {i:2}. [{count}] {title}")
        
        print(f"\n" + "=" * 60)
        print(f"✅ Done! Check: https://ai-news-frontend-d1ld.onrender.com")
        print(f"=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
