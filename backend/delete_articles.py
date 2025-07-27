#!/usr/bin/env python3
"""
Script to delete rows 47-69 from the NewsArticle database
"""

from app.database import get_db
from app.models import NewsArticle
from sqlalchemy.orm import Session

def delete_articles_1_and_2():
    """Delete rows 1 and 2 (indices 0 and 1)"""
    db = next(get_db())
    
    try:
        # Get articles from row 1 to 2 (offset 0, limit 2)
        articles = db.query(NewsArticle).offset(0).limit(2).all()
        
        if not articles:
            print("No articles found in rows 1-2.")
            return
        
        print(f"Found {len(articles)} articles to delete:")
        print("-" * 50)
        
        for i, article in enumerate(articles):
            print(f"  {i+1}. {article.title[:60]}...")
            print(f"      URL: {article.url}")
            print(f"      Source: {article.source}")
            print(f"      Created: {article.created_at}")
            print()
        
        # Ask for confirmation
        confirm = input("Delete these articles? (y/N): ")
        
        if confirm.lower() == 'y':
            # Delete each article
            for article in articles:
                db.delete(article)
            
            # Commit the changes
            db.commit()
            print(f"✅ Successfully deleted {len(articles)} articles!")
        else:
            print("❌ Deletion cancelled.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    delete_articles_1_and_2() 