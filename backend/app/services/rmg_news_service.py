from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from ..models import NewsArticle
from ..database import get_db
import asyncio
from .agno_service import agno_service

class RMGNewsService:
    """Service to fetch and store RMG news from multiple sources"""
    
    def __init__(self):
        self.sources = {
            "textiletoday": {
                "name": "Textile Today",
                "url": "https://www.textiletoday.com.bd/category/news-analysis-textile-apparel",
                "base_url": "https://www.textiletoday.com.bd"
            },
            "tbsnews": {
                "name": "TBS News RMG",
                "url": "http://tbsnews.net/economy/rmg",
                "base_url": "http://tbsnews.net"
            },
            "rmgbd": {
                "name": "RMG Bangladesh",
                "url": "https://rmgbd.net/",
                "base_url": "https://rmgbd.net"
            },
            "bgmea": {
                "name": "BGMEA",
                "url": "https://www.bgmea.com.bd/page/all-news",
                "base_url": "https://www.bgmea.com.bd"
            },
            "financialexpress": {
                "name": "Financial Express RMG",
                "url": "https://today.thefinancialexpress.com.bd/special-issues/rmg-textile",
                "base_url": "https://today.thefinancialexpress.com.bd"
            },
            "textilefocus": {
                "name": "Textile Focus",
                "url": "https://textilefocus.com/",
                "base_url": "https://textilefocus.com"
            }
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def fetch_all_sources(self, db: Session, articles_per_source: int = 15) -> Dict[str, int]:
        """Fetch news from all sources and store immediately"""
        results = {}
        
        # Fetch from all sources sequentially (to avoid database session conflicts)
        for source_id, source_info in self.sources.items():
            try:
                print(f"Fetching from {source_info['name']}...")
                articles = await self.fetch_from_source(source_id, source_info, articles_per_source, db)
                results[source_id] = len(articles)
                print(f"Fetched {len(articles)} articles from {source_info['name']}")
            except Exception as e:
                print(f"Error fetching from {source_info['name']}: {str(e)}")
                results[source_id] = 0
        
        return results

    async def fetch_from_source(self, source_id: str, source_info: Dict, max_articles: int, db: Session) -> List[Dict]:
        """Fetch articles from a specific source using Agno and store immediately"""
        try:
            print(f"Using Agno to scrape {source_info['name']}...")
            
            # Create callback function for immediate storage
            async def store_callback(article: Dict, db_session: Session) -> bool:
                # Add source information to article
                article['source_id'] = source_id
                article['source_info'] = source_info
                article['author'] = article.get('author', source_info['name'])
                
                # Store the article immediately
                return await self.store_single_article(article, db_session)
            
            # Use Agno to scrape the website with immediate storage
            articles = await agno_service.scrape_news_website(
                source_info['url'], 
                max_articles,
                db=db,
                store_callback=store_callback
            )
            
            print(f"Agno scraped {len(articles)} articles from {source_info['name']}")
            return articles
            
        except Exception as e:
            print(f"Error fetching from {source_info['name']} with Agno: {str(e)}")
            return []



    async def store_single_article(self, article_data: Dict, db: Session) -> bool:
        """Store a single article in database immediately (duplicate check already done)"""
        try:
            # Create new article (duplicate check was already done in agno_service)
            article = NewsArticle(
                title=article_data['title'],
                content=article_data['content'],
                summary=article_data['content'][:200] + "..." if len(article_data['content']) > 200 else article_data['content'],
                url=article_data['url'],
                source=article_data['source_id'],
                source_url=article_data['source_info']['url'],
                author=article_data.get('author', ''),
                published_at=article_data['published_at'],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Store immediately
            db.add(article)
            db.commit()
            print(f"  💾 Successfully stored article: {article_data['title'][:50]}...")
            return True
            
        except Exception as e:
            print(f"  ❌ Error storing article: {str(e)}")
            db.rollback()
            return False

    async def store_articles_batch(self, db: Session, articles: List[Dict]) -> int:
        """Store articles in database using batch operations (legacy method)"""
        stored_count = 0
        new_articles = []
        
        # Get all existing URLs in one query
        urls = [article['url'] for article in articles]
        existing_urls = set()
        if urls:
            existing = db.query(NewsArticle.url).filter(NewsArticle.url.in_(urls)).all()
            existing_urls = {row[0] for row in existing}
        
        # Prepare new articles
        for article_data in articles:
            try:
                if article_data['url'] not in existing_urls:
                    # Create new article
                    article = NewsArticle(
                        title=article_data['title'],
                        content=article_data['content'],
                        summary=article_data['content'][:200] + "..." if len(article_data['content']) > 200 else article_data['content'],
                        url=article_data['url'],
                        source=article_data['source_id'],
                        source_url=article_data['source_info']['url'],
                        author=article_data.get('author', ''),
                        published_at=article_data['published_at'],
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
                    new_articles.append(article)
                    stored_count += 1
                
            except Exception as e:
                print(f"Error preparing article: {str(e)}")
                continue
        
        # Batch insert all new articles
        if new_articles:
            try:
                db.add_all(new_articles)
                db.commit()
                print(f"Batch stored {stored_count} new articles")
            except Exception as e:
                print(f"Error committing to database: {str(e)}")
                db.rollback()
                stored_count = 0
        
        return stored_count

    def get_sources(self) -> Dict[str, Dict]:
        """Get available sources"""
        return self.sources

# Create service instance
rmg_news_service = RMGNewsService() 