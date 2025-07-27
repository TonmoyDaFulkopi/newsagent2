from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.sql import func
from .database import Base

class NewsArticle(Base):
    """News article model"""
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    url = Column(String(1000), unique=True, nullable=False)
    source = Column(String(200), nullable=False)  # Source name (e.g., "textiletoday", "tbsnews")
    source_url = Column(String(200), nullable=False)  # Full source URL
    author = Column(String(200), nullable=True)
    published_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # AI Analysis fields
    ai_summary = Column(Text, nullable=True)  # AI-generated summary
    market_impact = Column(String(50), nullable=True)  # high, medium, low
    confidence_score = Column(Float, nullable=True)  # AI confidence (0-1)
    is_processed = Column(Boolean, default=False)  # Whether AI analysis is done 