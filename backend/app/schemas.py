from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, List
from enum import Enum

class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class MarketImpact(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# Base schemas
class NewsArticleBase(BaseModel):
    title: str = Field(..., max_length=500)
    content: Optional[str] = None
    summary: Optional[str] = None
    url: HttpUrl
    source: str = Field(..., max_length=200)
    author: Optional[str] = Field(None, max_length=200)
    published_at: datetime

class NewsArticleCreate(NewsArticleBase):
    pass

class NewsArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    summary: Optional[str] = None
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1)
    sentiment_label: Optional[SentimentLabel] = None
    relevance_score: Optional[float] = Field(None, ge=0, le=1)
    is_processed: Optional[bool] = None

class NewsArticle(NewsArticleBase):
    id: int
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[SentimentLabel] = None
    relevance_score: Optional[float] = None
    is_processed: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Topic schemas
class TopicBase(BaseModel):
    name: str = Field(..., max_length=200)
    category: str = Field(..., max_length=100)
    description: Optional[str] = None

class TopicCreate(TopicBase):
    pass

class Topic(TopicBase):
    id: int
    is_trending: bool = False
    trend_score: float = 0.0
    created_at: datetime

    class Config:
        from_attributes = True

# Analysis schemas
class NewsAnalysisBase(BaseModel):
    key_insights: Optional[str] = None
    market_impact: Optional[MarketImpact] = None
    industry_sectors: Optional[str] = None  # JSON string
    geographic_impact: Optional[str] = None  # JSON string

class NewsAnalysisCreate(NewsAnalysisBase):
    article_id: int

class NewsAnalysis(NewsAnalysisBase):
    id: int
    article_id: int
    agno_analysis_id: Optional[str] = None
    agno_confidence: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Market trend schemas
class MarketTrendBase(BaseModel):
    metric_name: str = Field(..., max_length=200)
    metric_value: float
    metric_unit: Optional[str] = Field(None, max_length=50)
    category: str = Field(..., max_length=100)
    time_period: str = Field(..., max_length=50)

class MarketTrendCreate(MarketTrendBase):
    source: Optional[str] = Field(None, max_length=200)
    confidence: Optional[float] = Field(None, ge=0, le=1)

class MarketTrend(MarketTrendBase):
    id: int
    recorded_at: datetime
    source: Optional[str] = None
    confidence: Optional[float] = None

    class Config:
        from_attributes = True

# Response schemas
class NewsResponse(BaseModel):
    articles: List[NewsArticle]
    total: int
    page: int = 1
    per_page: int = 10

class AnalysisResponse(BaseModel):
    success: bool
    message: str
    analysis_id: Optional[str] = None

class TrendingTopicsResponse(BaseModel):
    topics: List[Topic]
    updated_at: datetime

class MarketInsightsResponse(BaseModel):
    sentiment_overview: dict
    trending_topics: List[Topic]
    market_trends: List[MarketTrend]
    total_articles: int
    last_updated: datetime 