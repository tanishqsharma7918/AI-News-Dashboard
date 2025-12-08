#!/usr/bin/env python3
"""
Seed new sources and fetch articles
Run this in Render Shell: python3 seed_and_fetch.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import seed
import fetcher

def main():
    print("=" * 60)
    print("🌱 SEEDING NEW AI/ML/GENAI SOURCES")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Seed new sources
        print("\n📥 Running seed_sources()...")
        seed.seed_sources()
        print("✅ Seeding complete!")
        
        # Count total sources
        import models
        total_sources = db.query(models.Source).filter_by(active=True).count()
        print(f"📊 Total active sources: {total_sources}")
        
        print("\n" + "=" * 60)
        print("📰 FETCHING ARTICLES FROM ALL SOURCES")
        print("=" * 60)
        
        # Fetch articles
        print("\n🔄 Fetching news from all 40 sources...")
        print("⏳ This may take 2-3 minutes...")
        new_items = fetcher.fetch_and_store_news(db)
        
        print("\n" + "=" * 60)
        print("✅ COMPLETE!")
        print("=" * 60)
        print(f"📊 New articles saved: {new_items}")
        
        # Count total articles
        total_articles = db.query(models.NewsItem).count()
        print(f"📊 Total articles in database: {total_articles}")
        
        print("\n💡 Next step: Run clustering to organize articles into topics")
        print("   curl -X POST https://ai-news-backend-age8.onrender.com/reset-clustering --max-time 300")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
