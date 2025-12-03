#!/usr/bin/env python3
"""
Standalone script to reset and re-cluster articles with debugging
Run this directly in Render shell: python3 reset_and_cluster.py
"""

from database import SessionLocal
import models
import clustering
import sys

def main():
    print("=" * 60)
    print("CLUSTERING RESET SCRIPT")
    print("=" * 60)
    
    # Show current configuration
    print(f"\n📋 Configuration:")
    print(f"   Threshold: {clustering.SIMILARITY_THRESHOLD}")
    print(f"   Model: {clustering.EMBED_MODEL}")
    
    db = SessionLocal()
    try:
        # Get initial counts
        initial_topics = db.query(models.Topic).count()
        initial_articles = db.query(models.NewsItem).count()
        print(f"\n📊 Before Reset:")
        print(f"   Topics: {initial_topics}")
        print(f"   Articles: {initial_articles}")
        
        # Reset
        print(f"\n🔄 Resetting database...")
        db.query(models.NewsItem).update({"topic_id": None})
        db.commit()
        print(f"   ✓ Cleared all topic assignments")
        
        deleted = db.query(models.Topic).delete()
        db.commit()
        print(f"   ✓ Deleted {deleted} topics")
        
        # Re-cluster
        print(f"\n🧠 Running clustering (this may take 1-2 minutes)...")
        print(f"   Using threshold: {clustering.SIMILARITY_THRESHOLD}")
        clustering.run_clustering(db)
        
        # Final counts
        final_topics = db.query(models.Topic).count()
        final_linked = db.query(models.NewsItem).filter(
            models.NewsItem.topic_id != None
        ).count()
        final_unlinked = db.query(models.NewsItem).filter(
            models.NewsItem.topic_id == None
        ).count()
        
        print(f"\n" + "=" * 60)
        print(f"📊 RESULTS:")
        print(f"=" * 60)
        print(f"   Topics created: {final_topics}")
        print(f"   Articles linked: {final_linked}")
        print(f"   Articles unlinked: {final_unlinked}")
        
        if final_topics > 0:
            ratio = final_linked / final_topics
            print(f"   Average per topic: {ratio:.1f}")
            
            if ratio < 1.5:
                print(f"\n⚠️  WARNING: Ratio is too low ({ratio:.1f})")
                print(f"   Threshold {clustering.SIMILARITY_THRESHOLD} might be too strict")
                print(f"   Recommendation: Try 0.60 or lower")
            elif ratio > 10:
                print(f"\n⚠️  WARNING: Ratio is too high ({ratio:.1f})")
                print(f"   Threshold {clustering.SIMILARITY_THRESHOLD} might be too loose")
                print(f"   Recommendation: Try 0.70 or higher")
            else:
                print(f"\n✅ Good ratio! Clustering looks healthy.")
        
        # Show sample topics
        print(f"\n📋 Sample Topics with Article Counts:")
        sample_topics = db.query(models.Topic).limit(10).all()
        for i, topic in enumerate(sample_topics, 1):
            article_count = db.query(models.NewsItem).filter(
                models.NewsItem.topic_id == topic.id
            ).count()
            title_short = topic.title[:50] + "..." if len(topic.title) > 50 else topic.title
            print(f"   {i}. [{article_count} articles] {title_short}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()
    
    print(f"\n" + "=" * 60)
    print(f"✅ Script completed successfully!")
    print(f"=" * 60)

if __name__ == "__main__":
    main()
