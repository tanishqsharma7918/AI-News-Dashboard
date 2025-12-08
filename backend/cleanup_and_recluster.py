#!/usr/bin/env python3
"""
Complete cleanup and re-clustering script
- Removes non-AI articles from database
- Resets all clustering
- Re-runs clustering with 0.78 threshold
Run in Render Shell: python3 cleanup_and_recluster.py
"""

from database import SessionLocal
import models
import clustering

def main():
    print("=" * 70)
    print("🧹 COMPLETE DATABASE CLEANUP & RE-CLUSTERING")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        # Step 1: Show initial state
        initial_articles = db.query(models.NewsItem).count()
        initial_topics = db.query(models.Topic).count()
        
        print(f"\n📊 Initial State:")
        print(f"   Articles: {initial_articles}")
        print(f"   Topics: {initial_topics}")
        
        # Step 2: Remove non-AI articles
        print(f"\n🧹 Step 1: Cleaning non-AI articles...")
        
        # Patterns to remove
        remove_patterns = [
            "i'm a junior dev",
            "just got laid off",
            "career advice",
            "job hunting",
            "how to climb",
            "self-promotion",
            "who's hiring",
            "monthly thread",
            "discussion thread",
            "yolov1 paper walkthrough",
            "bootstrap a data lakehouse",
            "the best data scientists",
            "how to design evals",
            "step-by-step process",
            "product data scientist's take",
            "career ladder",
        ]
        
        removed_count = 0
        all_articles = db.query(models.NewsItem).all()
        
        for article in all_articles:
            text = f"{article.title} {article.summary}".lower()
            
            # Check if it matches removal patterns
            should_remove = False
            for pattern in remove_patterns:
                if pattern in text:
                    should_remove = True
                    break
            
            # Also remove if it doesn't contain AI keywords
            if not should_remove:
                if not clustering.contains_ai_keyword(text):
                    should_remove = True
            
            # Remove meta/reddit threads
            if not should_remove:
                if clustering.is_meta_or_non_ai_thread(text):
                    should_remove = True
            
            if should_remove:
                title_short = article.title[:60] + "..." if len(article.title) > 60 else article.title
                print(f"   ❌ Removing: {title_short}")
                db.delete(article)
                removed_count += 1
        
        db.commit()
        print(f"   ✅ Removed {removed_count} non-AI articles")
        
        # Step 3: Reset clustering
        print(f"\n🔄 Step 2: Resetting clustering...")
        db.query(models.NewsItem).update({"topic_id": None})
        db.commit()
        print(f"   ✅ Cleared all topic assignments")
        
        deleted_topics = db.query(models.Topic).delete()
        db.commit()
        print(f"   ✅ Deleted {deleted_topics} old topics")
        
        # Step 4: Re-cluster with new threshold
        remaining_articles = db.query(models.NewsItem).count()
        print(f"\n🧠 Step 3: Re-clustering {remaining_articles} articles...")
        print(f"   Threshold: {clustering.SIMILARITY_THRESHOLD}")
        print(f"   Model: {clustering.EMBED_MODEL}")
        print(f"   ⏳ This will take 2-3 minutes...")
        
        try:
            clustering.run_clustering(db)
        except Exception as e:
            print(f"\n⚠️  Clustering error (continuing to show results): {e}")
        
        # Step 5: Show final results
        final_articles = db.query(models.NewsItem).count()
        final_topics = db.query(models.Topic).count()
        linked = db.query(models.NewsItem).filter(models.NewsItem.topic_id != None).count()
        unlinked = db.query(models.NewsItem).filter(models.NewsItem.topic_id == None).count()
        
        print(f"\n" + "=" * 70)
        print(f"📊 FINAL RESULTS:")
        print(f"=" * 70)
        print(f"   Articles before cleanup:  {initial_articles}")
        print(f"   Articles removed:         {removed_count}")
        print(f"   Articles remaining:       {final_articles}")
        print(f"   ")
        print(f"   Topics created:           {final_topics}")
        print(f"   Articles linked:          {linked}")
        print(f"   Articles unlinked:        {unlinked}")
        
        if final_topics > 0 and linked > 0:
            ratio = linked / final_topics
            print(f"   Average per topic:        {ratio:.1f}")
            print(f"")
            
            if ratio < 2:
                print(f"   ⚠️  Status: Too granular (try lowering threshold to 0.72)")
            elif ratio > 10:
                print(f"   ⚠️  Status: Too broad (try raising threshold to 0.82)")
            else:
                print(f"   ✅ Status: HEALTHY CLUSTERING!")
        
        # Show top topics
        print(f"\n🔥 Top 10 Popular Topics:")
        top_topics = db.query(models.Topic).order_by(
            models.Topic.popularity_score.desc()
        ).limit(10).all()
        
        for i, topic in enumerate(top_topics, 1):
            article_count = db.query(models.NewsItem).filter_by(topic_id=topic.id).count()
            title_short = topic.title[:55] + "..." if len(topic.title) > 55 else topic.title
            print(f"   {i:2}. [{article_count} articles] {title_short}")
        
        print(f"\n" + "=" * 70)
        print(f"✅ CLEANUP & CLUSTERING COMPLETE!")
        print(f"=" * 70)
        print(f"\n🌐 Check your frontend:")
        print(f"   https://ai-news-frontend-d1ld.onrender.com")
        print(f"")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
