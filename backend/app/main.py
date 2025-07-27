from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import asyncio
from dotenv import load_dotenv
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

# Import our modules
from .database import engine, get_db
from .models import Base, NewsArticle
from .schemas import (
    MarketInsightsResponse, Topic, NewsResponse, TrendingTopicsResponse,
    NewsAnalysis
)
from .services.agno_service import agno_service
from .services.rmg_news_service import rmg_news_service

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI instance
app = FastAPI(
    title="RMG News AI Agent API",
    description="A sophisticated AI-powered news aggregation and analysis platform for the Ready-Made Garment industry",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add pagination helper function
def create_paginated_response(articles: List, total: int, page: int, per_page: int) -> dict:
    """Create a paginated response with metadata"""
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "articles": articles,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "next_page": page + 1 if has_next else None,
        "prev_page": page - 1 if has_prev else None
    }

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Welcome to RMG News AI Agent API",
        "status": "healthy",
        "version": "1.0.0",
        "features": [
            "AI-Powered News Analysis",
            "Market Intelligence Dashboard", 
            "Trending Topics Detection"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "API is running successfully",
        "database": "connected",
        "deepseek_service": "configured"
    }

@app.get("/api/news", response_model=NewsResponse)
async def get_news(
    page: int = 1,
    per_page: int = 10,
    query: Optional[str] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get RMG news articles from database with pagination"""
    try:
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        # Build query
        query_builder = db.query(NewsArticle)
        
        # Filter by source if specified
        if source:
            query_builder = query_builder.filter(NewsArticle.source == source)
        
        # Filter by search query if specified
        if query:
            query_builder = query_builder.filter(
                NewsArticle.title.contains(query) | 
                NewsArticle.content.contains(query) |
                NewsArticle.summary.contains(query)
            )
        
        # Get total count
        total = query_builder.count()
        
        # Apply pagination
        articles = query_builder.order_by(NewsArticle.published_at.desc()) \
                               .offset((page - 1) * per_page) \
                               .limit(per_page) \
                               .all()
        
        return create_paginated_response(articles, total, page, per_page)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {str(e)}")

@app.get("/api/headlines", response_model=NewsResponse)
async def get_headlines(
    category: str = "business",
    country: str = "us",
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db)
):
    """Get top business headlines from database with pagination"""
    try:
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        # Query articles from database
        query_builder = db.query(NewsArticle)
        
        # Filter by category if specified
        if category and category != "business":
            if category.lower() in ["rmg", "textile", "garment"]:
                query_builder = query_builder.filter(
                    NewsArticle.source.in_(list(rmg_news_service.get_sources().keys()))
                )
        
        # Get total count
        total = query_builder.count()
        
        # Apply pagination
        headlines = query_builder.order_by(NewsArticle.published_at.desc()) \
                                .offset((page - 1) * per_page) \
                                .limit(per_page) \
                                .all()
        
        return create_paginated_response(headlines, total, page, per_page)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch headlines: {str(e)}")


class AnalyzeRequest(BaseModel):
    article_text: str
    title: str

@app.post("/api/analyze", response_model=NewsAnalysis)
async def analyze_article(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """Analyze a news article using AI"""
    try:
        analysis_data = await agno_service.analyze_article(request.article_text, request.title)
        
        # Convert to NewsAnalysis object
        analysis = NewsAnalysis(
            id=1,  # Simple ID generation
            article_id=1,  # Would be linked to actual article in real implementation
            key_insights=analysis_data.get("key_insights", ""),
            market_impact=analysis_data.get("market_impact", "medium"),
            industry_sectors=str(analysis_data.get("industry_sectors", [])),
            geographic_impact=analysis_data.get("geographic_impact", ""),
            agno_analysis_id=analysis_data.get("analysis_id", ""),
            agno_confidence=analysis_data.get("confidence", 0.0),
            created_at=datetime.now()
        )
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze article: {str(e)}")

@app.get("/api/sentiment")
async def get_sentiment_analysis(
    text: str,
    db: Session = Depends(get_db)
):
    """Get sentiment analysis for text"""
    try:
        analysis_data = await agno_service.analyze_article(text, "Sentiment Analysis")
        
        return {
            "sentiment": analysis_data.get("sentiment", {}),
            "confidence": analysis_data.get("confidence", 0.0),
            "method": analysis_data.get("method", "unknown")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze sentiment: {str(e)}")

@app.get("/api/trending", response_model=TrendingTopicsResponse)
async def get_trending_topics(
    hours_back: int = 24,
    db: Session = Depends(get_db)
):
    """Get trending topics in RMG industry from database"""
    try:
        # Get recent articles from database for trending analysis
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        articles = db.query(NewsArticle).filter(
            NewsArticle.published_at >= cutoff_time
        ).order_by(NewsArticle.published_at.desc()).limit(20).all()
        
        # Prepare article texts for analysis
        article_texts = []
        for article in articles:
            if article.content and article.title:
                article_texts.append(f"{article.title} {article.content}")
        
        trending_data = await agno_service.identify_trending_topics(article_texts[:10])
        
        # Convert to Topic objects
        topics = []
        for topic_data in trending_data:
            topic = Topic(
                id=len(topics) + 1,
                name=topic_data.get("name", ""),
                category=topic_data.get("category", "General"),
                is_trending=True,
                trend_score=topic_data.get("score", 0),
                created_at=datetime.now()
            )
            topics.append(topic)
        
        return TrendingTopicsResponse(
            topics=topics,
            updated_at=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trending topics: {str(e)}")

@app.get("/api/sources")
async def get_sources():
    """Get available news sources"""
    try:
        sources = rmg_news_service.get_sources()
        return {
            "sources": sources,
            "total": len(sources)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sources: {str(e)}")

@app.post("/api/fetch-news")
async def fetch_news_from_sources(
    articles_per_source: int = 15,
    db: Session = Depends(get_db)
):
    """Fetch news from all sources and store in database"""
    try:
        results = await rmg_news_service.fetch_all_sources(db, articles_per_source)
        
        return {
            "message": "News fetching completed",
            "results": results,
            "total_articles": sum(results.values()),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {str(e)}")

@app.get("/api/news/sources/{source_id}")
async def get_news_by_source(
    source_id: str,
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db)
):
    """Get news articles from a specific source with pagination"""
    try:
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        # Validate source
        sources = rmg_news_service.get_sources()
        if source_id not in sources:
            raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found")
        
        # Query articles from specific source
        query_builder = db.query(NewsArticle).filter(NewsArticle.source == source_id)
        total = query_builder.count()
        
        # Apply pagination
        articles = query_builder.order_by(NewsArticle.published_at.desc()) \
                               .offset((page - 1) * per_page) \
                               .limit(per_page) \
                               .all()
        
        return create_paginated_response(articles, total, page, per_page)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch news from source: {str(e)}")

@app.get("/api/insights", response_model=MarketInsightsResponse)
async def get_market_insights(db: Session = Depends(get_db)):
    """Get comprehensive market insights dashboard data"""
    try:
        # Get articles from database
        articles = db.query(NewsArticle).order_by(NewsArticle.published_at.desc()).limit(20).all()
        
        # Get trending topics from recent articles
        article_texts = [f"{article.title} {article.content}" for article in articles if article.content]
        trending_data = await agno_service.identify_trending_topics(article_texts[:10])
        
        # Convert trending data to Topic objects
        topics = []
        for topic_data in trending_data:
            topic = Topic(
                id=len(topics) + 1,
                name=topic_data.get("name", ""),
                category=topic_data.get("category", "General"),
                is_trending=True,
                trend_score=topic_data.get("score", 0),
                created_at=datetime.now()
            )
            topics.append(topic)
        
        # Calculate sentiment overview from database articles
        sentiment_overview = {}
        if articles:
            # Analyze a sample of articles for sentiment in parallel
            sample_articles = articles[:5]
            
            # Create analysis tasks
            analysis_tasks = []
            for article in sample_articles:
                task = agno_service.analyze_article(
                    article.content or '', 
                    article.title
                )
                analysis_tasks.append(task)
            
            # Run all analyses in parallel
            analyses = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for analysis in analyses:
                if isinstance(analysis, Exception):
                    neutral_count += 1  # Default to neutral on error
                    continue
                    
                sentiment = analysis.get('sentiment', {}).get('label', 'neutral')
                if sentiment == 'positive':
                    positive_count += 1
                elif sentiment == 'negative':
                    negative_count += 1
                else:
                    neutral_count += 1
            
            total = len(sample_articles)
            sentiment_overview = {
                "positive": f"{positive_count}/{total}",
                "negative": f"{negative_count}/{total}",
                "neutral": f"{neutral_count}/{total}"
            }
        
        return MarketInsightsResponse(
            sentiment_overview=sentiment_overview,
            trending_topics=topics,
            market_trends=[],  # Will be populated when we have trend data
            total_articles=len(articles),
            last_updated=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get market insights: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 