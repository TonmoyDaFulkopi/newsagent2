// API service for RMG News AI backend

const API_BASE_URL = 'http://localhost:8000';

// Add timeout to fetch requests with longer timeouts
const fetchWithTimeout = async (url: string, options: RequestInit = {}, timeout: number = 30000) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error(`Request timeout after ${timeout}ms`);
    }
    throw error;
  }
};

export interface NewsArticle {
  id: number;
  title: string;
  content: string;
  summary: string;
  url: string;
  source: string;
  source_url: string;
  author: string;
  published_at: string;
  created_at: string;
  updated_at: string;
  ai_summary?: string | null;
  market_impact?: string | null;
  confidence_score?: number | null;
  is_processed?: boolean;
}

export interface NewsSource {
  name: string;
  url: string;
  base_url: string;
}

export interface SourcesResponse {
  sources: { [key: string]: NewsSource };
  total: number;
}

export interface NewsResponse {
  articles: NewsArticle[];
  total: number;
  page: number;
  per_page: number;
}

export interface Topic {
  id: number;
  name: string;
  category: string;
  is_trending: boolean;
  trend_score: number;
  created_at: string;
}

export interface TrendingTopicsResponse {
  topics: Topic[];
  updated_at: string;
}

export interface MarketTrend {
  id: number;
  metric_name: string;
  metric_value: number;
  metric_unit?: string;
  category: string;
  time_period: string;
  recorded_at: string;
  source?: string;
  confidence?: number;
}

export interface MarketInsightsResponse {
  sentiment_overview: {
    positive: string;
    negative: string;
    neutral: string;
  };
  trending_topics: Topic[];
  market_trends: MarketTrend[];
  total_articles: number;
  last_updated: string;
}

export interface NewsAnalysis {
  id: number;
  article_id: number;
  key_insights: string;
  market_impact: string;
  industry_sectors: string;
  geographic_impact: string;
  agno_analysis_id: string;
  agno_confidence: number;
  created_at: string;
}

// API Functions
export const api = {
  // Get news articles
  async getNews(query?: string, page: number = 1, perPage: number = 10, source?: string): Promise<NewsResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
    });
    
    if (query) {
      params.append('query', query);
    }
    
    if (source) {
      params.append('source', source);
    }
    
    console.log(`Fetching news from: ${API_BASE_URL}/api/news?${params}`);
    
    const response = await fetchWithTimeout(`${API_BASE_URL}/api/news?${params}`, {}, 45000);
    if (!response.ok) {
      throw new Error(`Failed to fetch news: ${response.status} ${response.statusText}`);
    }
    return response.json();
  },

  // Get news by source
  async getNewsBySource(sourceId: string, page: number = 1, perPage: number = 10): Promise<NewsResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
    });
    
    console.log(`Fetching news from source ${sourceId}: ${API_BASE_URL}/api/news/sources/${sourceId}?${params}`);
    
    const response = await fetchWithTimeout(`${API_BASE_URL}/api/news/sources/${sourceId}?${params}`, {}, 45000);
    if (!response.ok) {
      throw new Error(`Failed to fetch news from source: ${response.status} ${response.statusText}`);
    }
    return response.json();
  },

  // Get available sources
  async getSources(): Promise<SourcesResponse> {
    console.log(`Fetching sources from: ${API_BASE_URL}/api/sources`);
    
    const response = await fetchWithTimeout(`${API_BASE_URL}/api/sources`, {}, 15000);
    if (!response.ok) {
      throw new Error(`Failed to fetch sources: ${response.status} ${response.statusText}`);
    }
    return response.json();
  },

  // Fetch news from all sources
  async fetchNewsFromSources(articlesPerSource: number = 15): Promise<{
    message: string;
    results: Record<string, number>;
    total_articles: number;
    timestamp: string;
  }> {
    console.log(`Fetching news from all sources: ${API_BASE_URL}/api/fetch-news`);
    
    const response = await fetchWithTimeout(`${API_BASE_URL}/api/fetch-news`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        articles_per_source: articlesPerSource,
      }),
    }, 120000); // 2 minutes timeout for fetching from all sources
    
    if (!response.ok) {
      throw new Error(`Failed to fetch news from sources: ${response.status} ${response.statusText}`);
    }
    return response.json();
  },

  // Get headlines by category
  async getHeadlines(category: string = 'business', country: string = 'us', pageSize: number = 10): Promise<NewsResponse> {
    const params = new URLSearchParams({
      category,
      country,
      page_size: pageSize.toString(),
    });
    
    console.log(`Fetching headlines from: ${API_BASE_URL}/api/headlines?${params}`);
    
    const response = await fetchWithTimeout(`${API_BASE_URL}/api/headlines?${params}`, {}, 45000);
    if (!response.ok) {
      throw new Error(`Failed to fetch headlines: ${response.status} ${response.statusText}`);
    }
    return response.json();
  },

  // Get trending topics
  async getTrendingTopics(hoursBack: number = 24): Promise<TrendingTopicsResponse> {
    const params = new URLSearchParams({
      hours_back: hoursBack.toString(),
    });
    
    console.log(`Fetching trending topics from: ${API_BASE_URL}/api/trending?${params}`);
    
    const response = await fetchWithTimeout(`${API_BASE_URL}/api/trending?${params}`, {}, 45000);
    if (!response.ok) {
      throw new Error(`Failed to fetch trending topics: ${response.status} ${response.statusText}`);
    }
    return response.json();
  },

  // Get market insights
  async getMarketInsights(): Promise<MarketInsightsResponse> {
    console.log(`Fetching market insights from: ${API_BASE_URL}/api/insights`);
    
    const response = await fetchWithTimeout(`${API_BASE_URL}/api/insights`, {}, 45000);
    if (!response.ok) {
      throw new Error(`Failed to fetch market insights: ${response.status} ${response.statusText}`);
    }
    return response.json();
  },

  // Analyze article
  async analyzeArticle(articleText: string, title: string): Promise<NewsAnalysis> {
    console.log(`Analyzing article: ${title}`);
    
    const response = await fetchWithTimeout(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        article_text: articleText,
        title: title,
      }),
    }, 60000); // Longer timeout for AI analysis
    
    if (!response.ok) {
      throw new Error(`Failed to analyze article: ${response.status} ${response.statusText}`);
    }
    return response.json();
  },

  // Get sentiment analysis
  async getSentimentAnalysis(text: string) {
    const params = new URLSearchParams({ text });
    console.log(`Analyzing sentiment for text`);
    
    const response = await fetchWithTimeout(`${API_BASE_URL}/api/sentiment?${params}`, {}, 45000);
    if (!response.ok) {
      throw new Error(`Failed to analyze sentiment: ${response.status} ${response.statusText}`);
    }
    return response.json();
  },

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetchWithTimeout(`${API_BASE_URL}/health`, {}, 20000);
      return response.ok;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  },
}; 