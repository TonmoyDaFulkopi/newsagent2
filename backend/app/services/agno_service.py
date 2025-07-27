import os
import requests
from typing import Dict, Optional, List
from datetime import datetime
import json
import logging
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
from sqlalchemy.orm import Session
from ..models import NewsArticle

logger = logging.getLogger(__name__)

class AgnoService:
    """Service for AI analysis using Deepseek V3 API"""
    
    def __init__(self):
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.deepseek_api_key}"
        }
    
    async def analyze_article(self, article_text: str, title: str) -> Dict:
        """
        Analyze a news article using Deepseek V3
        
        Args:
            article_text: The full text of the article
            title: The article title
            
        Returns:
            Dict containing analysis results
        """
        if not self.deepseek_api_key:
            logger.warning("Deepseek API key not configured, using fallback analysis")
            return self._get_fallback_analysis(article_text, title)
        
        try:
            prompt = f"""
            Analyze this RMG (Ready-Made Garment) industry news article and provide detailed insights.
            
            Title: {title}
            Article: {article_text}
            
            Please provide analysis in the following JSON format:
            {{
                "sentiment": {{
                    "label": "positive/negative/neutral",
                    "score": -1.0 to 1.0,
                    "confidence": 0.0 to 1.0
                }},
                "key_insights": "2-3 key insights about the article",
                "market_impact": "high/medium/low",
                "topics": ["topic1", "topic2", "topic3"],
                "geographic_impact": "regions affected",
                "industry_sectors": ["sector1", "sector2"],
                "business_implications": "what this means for businesses"
            }}
            
            Focus on the RMG industry context and provide actionable insights.
            """
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert analyst specializing in the Ready-Made Garment (RMG) industry. Provide accurate, insightful analysis of news articles with focus on market impact, trends, and business implications. Always respond with valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            response = requests.post(
                self.deepseek_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Try to parse JSON response
                try:
                    analysis_data = json.loads(content)
                    return {
                        "analysis_id": f"deepseek_{datetime.now().timestamp()}",
                        "sentiment": analysis_data.get("sentiment", {}),
                        "key_insights": analysis_data.get("key_insights", ""),
                        "market_impact": analysis_data.get("market_impact", "medium"),
                        "topics": analysis_data.get("topics", []),
                        "geographic_impact": analysis_data.get("geographic_impact", ""),
                        "industry_sectors": analysis_data.get("industry_sectors", []),
                        "business_implications": analysis_data.get("business_implications", ""),
                        "confidence": analysis_data.get("sentiment", {}).get("confidence", 0.8),
                        "method": "deepseek"
                    }
                except json.JSONDecodeError:
                    # If JSON parsing fails, extract insights from text
                    return self._parse_deepseek_text_response(content, article_text, title)
            else:
                logger.error(f"Deepseek API error: {response.status_code} - {response.text}")
                return self._get_fallback_analysis(article_text, title)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Deepseek API request failed: {str(e)}")
            return self._get_fallback_analysis(article_text, title)
    
    def _parse_deepseek_text_response(self, content: str, article_text: str, title: str) -> Dict:
        """Parse Deepseek text response when JSON parsing fails"""
        # Simple sentiment detection from text
        text_lower = content.lower()
        if any(word in text_lower for word in ["positive", "growth", "increase", "success"]):
            sentiment = "positive"
            score = 0.7
        elif any(word in text_lower for word in ["negative", "decline", "crisis", "problem"]):
            sentiment = "negative"
            score = -0.7
        else:
            sentiment = "neutral"
            score = 0.0
        
        return {
            "analysis_id": f"deepseek_text_{datetime.now().timestamp()}",
            "sentiment": {
                "label": sentiment,
                "score": score,
                "confidence": 0.7
            },
            "key_insights": content[:200] + "..." if len(content) > 200 else content,
            "market_impact": "medium",
            "topics": self._extract_simple_topics(article_text.lower()),
            "confidence": 0.7,
            "method": "deepseek_text"
        }


    
    async def identify_trending_topics(self, article_texts: List[str]) -> List[Dict]:
        """
        Identify trending topics using Deepseek V3
        
        Args:
            article_texts: List of article texts to analyze
            
        Returns:
            List of trending topics with scores
        """
        if not self.deepseek_api_key:
            return self._get_fallback_topics()
        
        try:
            combined_text = " ".join(article_texts[:5])  # Limit to avoid token limits
            
            prompt = f"""
            Analyze these RMG industry articles and identify the top 5 trending topics:
            
            Articles: {combined_text}
            
            Please provide analysis in JSON format:
            {{
                "topics": [
                    {{"name": "topic_name", "category": "category", "score": 0.0 to 1.0}},
                    ...
                ]
            }}
            """
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert in identifying trending topics in the Ready-Made Garment industry. Always respond with valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 500
            }
            
            response = requests.post(
                self.deepseek_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                try:
                    topics_data = json.loads(content)
                    return topics_data.get("topics", [])
                except json.JSONDecodeError:
                    return self._get_fallback_topics()
            else:
                return self._get_fallback_topics()
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Trending topics API failed: {str(e)}")
            return self._get_fallback_topics()
    
    def _get_fallback_analysis(self, article_text: str, title: str) -> Dict:
        """Fallback analysis when Agno is unavailable"""
        # Simple keyword-based sentiment analysis
        positive_keywords = ["growth", "increase", "profit", "expansion", "success", "boost", "rise"]
        negative_keywords = ["decline", "loss", "crisis", "drop", "fall", "recession", "problem"]
        
        text_lower = (article_text + " " + title).lower()
        
        positive_score = sum(1 for word in positive_keywords if word in text_lower)
        negative_score = sum(1 for word in negative_keywords if word in text_lower)
        
        if positive_score > negative_score:
            sentiment = "positive"
            score = min(0.8, positive_score * 0.1)
        elif negative_score > positive_score:
            sentiment = "negative"
            score = max(-0.8, -negative_score * 0.1)
        else:
            sentiment = "neutral"
            score = 0.0
        
        return {
            "analysis_id": f"fallback_{datetime.now().timestamp()}",
            "sentiment": {
                "label": sentiment,
                "score": score,
                "confidence": 0.6
            },
            "key_insights": "Analysis performed using fallback method due to Agno unavailability.",
            "market_impact": "medium" if abs(score) > 0.3 else "low",
            "topics": self._extract_simple_topics(text_lower),
            "confidence": 0.6,
            "method": "fallback"
        }
    

    
    def _get_fallback_topics(self) -> List[Dict]:
        """Fallback trending topics"""
        return [
            {"name": "Ready-Made Garments", "category": "RMG", "score": 0.7},
            {"name": "Textile Industry", "category": "Manufacturing", "score": 0.6},
            {"name": "Fashion Trends", "category": "Fashion", "score": 0.5}
        ]
    
    def _extract_simple_topics(self, text: str) -> List[str]:
        """Simple topic extraction"""
        rmg_keywords = [
            "garment", "textile", "fashion", "apparel", "clothing",
            "manufacturing", "export", "cotton", "fabric", "factory"
        ]
        
        found_topics = []
        for keyword in rmg_keywords:
            if keyword in text:
                found_topics.append(keyword.title())
        
        return found_topics[:5]  # Limit to 5 topics

    async def scrape_news_website(self, url: str, max_articles: int = 15, db: Session = None, store_callback=None) -> List[Dict]:
        """
        Scrape news articles from a website with full content extraction using web scraping + AI analysis
        
        Args:
            url: The website URL to scrape
            max_articles: Maximum number of articles to extract
            db: Database session for immediate storage
            store_callback: Callback function to store articles immediately
            
        Returns:
            List of article dictionaries with full content
        """
        print(f"🚀 Starting to scrape: {url}")
        try:
            # Step 1: Extract article links from the main page using web scraping
            print(f"📋 Step 1: Extracting article links from {url}")
            article_links = await self._scrape_article_links(url, max_articles)
            
            if not article_links:
                print(f"❌ No article links found on {url}")
                logger.warning(f"No article links found on {url}")
                return []
            
            print(f"✅ Found {len(article_links)} article links")
            
            # Step 2: Extract full content from each article
            print(f"📄 Step 2: Extracting content from {len(article_links)} articles")
            articles = []
            stored_count = 0
            for i, link_data in enumerate(article_links[:max_articles]):
                try:
                    print(f"  📖 Processing article {i+1}/{len(article_links)}: {link_data['url']}")
                    
                    # Check for duplicates BEFORE content extraction and AI cleaning
                    if store_callback and db:
                        # Create a minimal article structure for duplicate check
                        check_article = {
                            "url": link_data['url'],
                            "title": link_data.get('title', ''),
                            "content": "",  # Will be filled later if not duplicate
                            "published_at": link_data.get('published_at', datetime.now()),
                            "author": link_data.get('author', '')
                        }
                        
                        # Quick duplicate check using URL only
                        try:
                            # Check if URL already exists in database
                            existing = db.query(NewsArticle).filter(NewsArticle.url == link_data['url']).first()
                            if existing:
                                print(f"  ⚠️  Article already exists (skipping): {link_data['url']}")
                                continue  # Skip this article entirely
                            else:
                                print(f"  ✅ Article is new, proceeding with extraction: {link_data['url']}")
                        except Exception as e:
                            print(f"  ❌ Error checking for duplicates: {str(e)}")
                            # Continue with extraction if duplicate check fails
                    
                    # Only extract content if article is new
                    full_content = await self._scrape_article_content(link_data['url'])
                    if full_content:
                        article = {
                            "title": link_data.get('title', full_content.get('title', '')),
                            "content": full_content.get('content', ''),
                            "url": link_data['url'],
                            "published_at": full_content.get('published_at', link_data.get('published_at', datetime.now())),
                            "author": full_content.get('author', link_data.get('author', ''))
                        }
                        articles.append(article)
                        
                        # Store article immediately if callback is provided
                        if store_callback and db:
                            try:
                                stored = await store_callback(article, db)
                                if stored:
                                    stored_count += 1
                                    print(f"  💾 Immediately stored article: {link_data['url']}")
                                else:
                                    print(f"  ⚠️  Article already exists or failed to store: {link_data['url']}")
                            except Exception as e:
                                print(f"  ❌ Error storing article: {str(e)}")
                        
                        print(f"  ✅ Successfully extracted content from: {link_data['url']}")
                        logger.info(f"Extracted content from: {link_data['url']}")
                    else:
                        print(f"  ⚠️  No content extracted from: {link_data['url']}")
                except Exception as e:
                    print(f"  ❌ Error extracting content from {link_data['url']}: {str(e)}")
                    logger.error(f"Error extracting content from {link_data['url']}: {str(e)}")
                    continue
            
            print(f"🎉 Successfully scraped {len(articles)} articles with full content from {url}")
            logger.info(f"Successfully scraped {len(articles)} articles with full content from {url}")
            return articles
                
        except Exception as e:
            print(f"💥 Web scraping failed for {url}: {str(e)}")
            logger.error(f"Web scraping failed for {url}: {str(e)}")
            return []

    async def _scrape_article_links(self, url: str, max_articles: int) -> List[Dict]:
        """Extract article links using web scraping"""
        print(f"  🔗 Fetching main page: {url}")
        try:
            # Fetch the main page with enhanced headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }
            
            print(f"  📡 Making HTTP request to {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            print(f"  ✅ HTTP request successful, status: {response.status_code}")
            
            # Check if we got actual content
            if len(response.content) < 1000:
                print(f"  ⚠️  Response content seems too small: {len(response.content)} bytes")
                print(f"  📄 Response content preview: {response.text[:200]}...")
            
            print(f"  🔍 Parsing HTML content...")
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"  ✅ HTML parsed successfully")
            
            # Debug: Print page title and some basic info
            page_title = soup.find('title')
            if page_title:
                print(f"  📄 Page title: {page_title.get_text(strip=True)}")
            
            # Debug: Count all links on the page
            all_links = soup.find_all('a', href=True)
            print(f"  🔗 Total links found on page: {len(all_links)}")
            
            # Debug: Show first few links for analysis
            print(f"  🔍 First 5 links on page:")
            for i, link in enumerate(all_links[:5]):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                print(f"    {i+1}. '{text[:50]}...' -> {href}")
            
            # Debug: Check if page content is loaded
            print(f"  🔍 Page content analysis:")
            print(f"    📄 HTML length: {len(response.content)} characters")
            print(f"    📄 Response encoding: {response.encoding}")
            
            # Debug: Look for specific content patterns
            page_text = soup.get_text()
            if "Oxford Knit Composite" in page_text:
                print(f"    ✅ Found expected content: 'Oxford Knit Composite'")
            else:
                print(f"    ❌ Expected content not found")
            
            # Debug: Check for common blocking patterns
            if "blocked" in page_text.lower() or "captcha" in page_text.lower():
                print(f"    ⚠️  Possible blocking detected")
            
            # Debug: Show some raw HTML for analysis
            print(f"  🔍 Sample HTML structure:")
            sample_html = str(soup)[:1000]
            print(f"    {sample_html[:200]}...")
            
            # Extract article links based on common patterns
            article_links = []
            
            # Look for article links in various selectors
            selectors = [
                # Generic article patterns
                'a[href*="/article/"]',
                'a[href*="/news/"]',
                'a[href*="/story/"]',
                'a[href*="/post/"]',
                'a[href*="/page/"]',
                'a[href*="/category/"]',
                
                # Common article containers
                'article a',
                '.article a',
                '.news-item a',
                '.post a',
                '.news a',
                '.content a',
                '.main-content a',
                
                # Headers with links
                'h1 a',
                'h2 a',
                'h3 a',
                'h4 a',
                '.entry-title a',
                '.post-title a',
                '.article-title a',
                '.headline a',
                '.title a',
                
                # Specific to BGMEA and Financial Express
                '.news-list a',
                '.news-container a',
                '.news-block a',
                '.news-section a',
                '.all-news a',
                '.special-issues a',
                '.rmg-textile a',
                
                # Textile Today specific (based on image analysis)
                '.category a',
                '.news-analysis a',
                '.textile-apparel a',
                '.main-content a',
                '.content-area a',
                '.article-list a',
                '.news-grid a',
                '.post-grid a',
                
                # WordPress specific (common for news sites)
                '.entry a',
                '.post a',
                '.blog-post a',
                '.news-post a',
                
                # Fallback: all links (will be filtered later)
                'a[href]'
            ]
            
            print(f"  🔍 Searching for article links using {len(selectors)} selectors...")
            all_found_links = []
            
            for i, selector in enumerate(selectors):
                print(f"    🔎 Trying selector {i+1}/{len(selectors)}: {selector}")
                links = soup.select(selector)
                print(f"    📊 Found {len(links)} links with selector: {selector}")
                
                for link in links:
                    href = link.get('href')
                    if href:
                        # Make URL absolute
                        full_url = urljoin(url, href)
                        
                        # Skip if already found
                        if any(link['url'] == full_url for link in all_found_links):
                            continue
                        
                        # Extract title
                        title = link.get_text(strip=True)
                        if not title:
                            # Try to find title in parent elements
                            parent = link.find_parent(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                            if parent:
                                title = parent.get_text(strip=True)
                        
                        # Debug: Show what we found
                        print(f"    🔍 Processing link: '{title[:50]}...' -> {full_url}")
                        
                        # IMMEDIATE NEWS LINK VALIDATION
                        is_valid_news_link = self._validate_news_link(title, full_url, href)
                        if not is_valid_news_link:
                            continue
                        
                        # Skip empty titles and very short titles
                        if not title or len(title) < 5:  # Reduced from 10 to 5
                            print(f"      ❌ Skipped: Title too short or empty (length: {len(title) if title else 0})")
                            continue
                        
                        # Skip navigation, footer, and other non-article links (relaxed)
                        if any(skip_word in title.lower() for skip_word in ['login', 'register', 'search']):  # Removed 'home', 'about', 'contact', 'menu', 'navigation'
                            print(f"      ❌ Skipped: Contains navigation word")
                            continue
                        
                        # Skip static content and contact information
                        static_content_patterns = [
                            'house-', 'road-', 'floor', 'dhaka', 'bangladesh',
                            'info@', '@', 'phone', 'tel:', 'fax:', 'email:',
                            'copyright', '©', 'all rights reserved', 'privacy',
                            'terms', 'contact us', 'about us', 'advertisement',
                            'subscribe', 'newsletter', 'social media', 'facebook',
                            'twitter', 'linkedin', 'youtube', 'instagram'
                        ]
                        
                        if any(pattern in title.lower() for pattern in static_content_patterns):
                            print(f"      ❌ Skipped: Static content/contact info")
                            continue
                        
                        # Skip very short or generic titles
                        if len(title) < 15 or title.lower() in ['read more', 'read original article', 'click here', 'learn more']:
                            print(f"      ❌ Skipped: Generic or too short title")
                            continue
                        
                        # Skip external links (optional) - but be more lenient
                        base_url = url.split('/page/')[0] if '/page/' in url else url
                        if not full_url.startswith(base_url):
                            print(f"      ❌ Skipped: External link (base: {base_url})")
                            continue
                        
                        # Additional check: Look for news-like patterns in the title
                        news_patterns = [
                            'announces', 'launches', 'reports', 'reveals', 'introduces',
                            'celebrates', 'partners', 'expands', 'invests', 'acquires',
                            'appoints', 'awards', 'recognizes', 'develops', 'innovates',
                            'challenges', 'opportunities', 'growth', 'development',
                            'industry', 'market', 'trade', 'export', 'import',
                            'technology', 'innovation', 'sustainability', 'compliance'
                        ]
                        
                        # Check if title contains news-like content
                        has_news_content = any(pattern in title.lower() for pattern in news_patterns)
                        
                        # Also check if title looks like a proper news headline (has proper capitalization, length)
                        looks_like_headline = (
                            len(title) >= 20 and 
                            len(title) <= 200 and
                            title[0].isupper() and
                            not title.isupper() and  # Not all caps
                            not title.islower()      # Not all lowercase
                        )
                        
                        if has_news_content or looks_like_headline:
                            all_found_links.append({
                                'title': title,
                                'url': full_url,
                                'published_at': datetime.now(),
                                'author': ''
                            })
                            print(f"    ✅ Added news-like link: {title[:50]}... -> {full_url}")
                        else:
                            print(f"    ⚠️  Skipped: Doesn't look like news content")
                
                # If we found links with this selector, don't try the fallback 'a[href]' selector
                if links and selector != 'a[href]':
                    break
            
            print(f"  📊 Total potential links found: {len(all_found_links)}")
            
            # Temporarily disable RMG filtering to see all links
            print(f"  🔍 Temporarily accepting all links for debugging...")
            for link_data in all_found_links:
                article_links.append(link_data)
                print(f"    ✅ Added article: {link_data['title'][:50]}...")
                
                if len(article_links) >= max_articles:
                    print(f"    🎯 Reached max articles limit ({max_articles})")
                    break
            
            print(f"  📊 Total article links found: {len(article_links)}")
            logger.info(f"Found {len(article_links)} article links on {url}")
            return article_links
            
        except Exception as e:
            print(f"  💥 Failed to scrape article links from {url}: {str(e)}")
            logger.error(f"Failed to scrape article links from {url}: {str(e)}")
            return []

    async def _scrape_article_content(self, article_url: str) -> Dict:
        """Extract full article content using web scraping + AI cleaning"""
        print(f"    📄 Fetching article content: {article_url}")
        try:
            # Fetch the article page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            print(f"    📡 Making HTTP request to article page...")
            response = requests.get(article_url, headers=headers, timeout=30)
            response.raise_for_status()
            print(f"    ✅ Article HTTP request successful, status: {response.status_code}")
            
            print(f"    🔍 Parsing article HTML...")
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"    ✅ Article HTML parsed successfully")
            
            # Extract title
            print(f"    📝 Extracting title...")
            title = self._extract_title(soup)
            print(f"    📝 Title: {title[:50]}..." if title else "    📝 No title found")
            
            # Extract content
            print(f"    📄 Extracting content...")
            content = self._extract_content(soup)
            print(f"    📄 Content length: {len(content) if content else 0} characters")
            
            # Extract metadata
            print(f"    📅 Extracting metadata...")
            published_at = self._extract_date(soup)
            author = self._extract_author(soup)
            print(f"    📅 Published: {published_at}, Author: {author}")
            
            # Use AI to clean the content if available
            if self.deepseek_api_key and content:
                print(f"    🤖 Using AI to clean content...")
                cleaned_content = await self._clean_content_with_ai(content, title)
                if cleaned_content:
                    content = cleaned_content
                    print(f"    🤖 AI cleaned content length: {len(content)} characters")
                else:
                    print(f"    ⚠️  AI cleaning failed, using original content")
            else:
                print(f"    ⚠️  No AI key or content, skipping AI cleaning")
            
            # Check if content looks like actual news (not static content)
            if content:
                # Check for static content patterns
                static_patterns = [
                    'house-', 'road-', 'floor', 'dhaka', 'bangladesh',
                    'info@', 'phone:', 'tel:', 'fax:', 'email:',
                    'copyright', '©', 'all rights reserved', 'privacy',
                    'terms', 'contact us', 'about us', 'advertisement'
                ]
                
                content_lower = content.lower()
                static_content_score = sum(1 for pattern in static_patterns if pattern in content_lower)
                
                # If more than 3 static patterns found, likely not a news article
                if static_content_score > 3:
                    print(f"    ❌ Content appears to be static/contact info (score: {static_content_score})")
                    logger.warning(f"Content appears to be static for {article_url}")
                    return None
                
                # Check for news-like content patterns
                news_patterns = [
                    'announces', 'launches', 'reports', 'reveals', 'introduces',
                    'celebrates', 'partners', 'expands', 'invests', 'acquires',
                    'appoints', 'awards', 'recognizes', 'develops', 'innovates',
                    'challenges', 'opportunities', 'growth', 'development',
                    'industry', 'market', 'trade', 'export', 'import'
                ]
                
                news_content_score = sum(1 for pattern in news_patterns if pattern in content_lower)
                
                if news_content_score < 1:
                    print(f"    ⚠️  Content doesn't contain news-like patterns (score: {news_content_score})")
            
            if not content or len(content) < 100:
                print(f"    ❌ Article content too short or missing ({len(content) if content else 0} chars)")
                logger.warning(f"Article content too short or missing for {article_url}")
                return None
            
            print(f"    ✅ Article content extracted successfully")
            return {
                "title": title,
                "content": content,
                "published_at": published_at,
                "author": author,
                "summary": content[:200] + "..." if len(content) > 200 else content
            }
            
        except Exception as e:
            print(f"    💥 Failed to scrape article content from {article_url}: {str(e)}")
            logger.error(f"Failed to scrape article content from {article_url}: {str(e)}")
            return None

    def _validate_news_link(self, title: str, full_url: str, href: str) -> bool:
        """
        Comprehensive validation to check if a link is actually a news article
        Returns True if it's a valid news link, False otherwise
        """
        if not title or not full_url:
            print(f"      ❌ Skipped: Missing title or URL")
            return False
        
        title_lower = title.lower()
        url_lower = full_url.lower()
        
        # 1. Check for obvious non-news patterns in title
        non_news_title_patterns = [
            # Navigation and UI elements
            'home', 'about', 'contact', 'login', 'register', 'sign up', 'sign in',
            'search', 'menu', 'navigation', 'footer', 'header', 'sidebar',
            'read more', 'read original article', 'click here', 'learn more',
            'subscribe', 'newsletter', 'advertisement', 'advertise',
            
            # Social media and external links
            'facebook', 'twitter', 'linkedin', 'youtube', 'instagram', 'whatsapp',
            'telegram', 'tiktok', 'snapchat', 'pinterest',
            
            # Contact and company info
            'house-', 'road-', 'floor', 'dhaka', 'bangladesh',
            'info@', '@', 'phone', 'tel:', 'fax:', 'email:',
            'copyright', '©', 'all rights reserved', 'privacy',
            'terms', 'contact us', 'about us', 'careers', 'jobs',
            
            # Generic actions
            'download', 'upload', 'share', 'print', 'bookmark', 'favorite',
            'like', 'comment', 'reply', 'follow', 'unfollow',
            
            # File types and media
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mp3', '.avi',
            
            # Common website elements
            'cookie', 'policy', 'disclaimer', 'sitemap', 'rss', 'feed',
            'archive', 'category', 'tag', 'author', 'date', 'time'
        ]
        
        for pattern in non_news_title_patterns:
            if pattern in title_lower:
                print(f"      ❌ Skipped: Non-news pattern '{pattern}' in title")
                return False
        
        # 2. Check URL patterns that indicate non-news content
        non_news_url_patterns = [
            '/login', '/register', '/signup', '/signin', '/account',
            '/cart', '/checkout', '/payment', '/billing',
            '/admin', '/dashboard', '/panel', '/control',
            '/api/', '/ajax/', '/json/', '/xml/',
            '/assets/', '/css/', '/js/', '/images/', '/uploads/',
            '/download/', '/upload/', '/media/',
            '/search', '/filter', '/sort', '/page/',
            '/tag/', '/category/', '/author/', '/date/',
            '/rss', '/feed', '/sitemap', '/robots.txt'
        ]
        
        for pattern in non_news_url_patterns:
            if pattern in url_lower:
                print(f"      ❌ Skipped: Non-news URL pattern '{pattern}'")
                return False
        
        # 3. Check for news-like patterns in title
        news_patterns = [
            # Action words
            'announces', 'launches', 'reports', 'reveals', 'introduces',
            'celebrates', 'partners', 'expands', 'invests', 'acquires',
            'appoints', 'awards', 'recognizes', 'develops', 'innovates',
            'challenges', 'opportunities', 'growth', 'development',
            'launches', 'releases', 'unveils', 'discloses', 'confirms',
            'denies', 'responds', 'comments', 'states', 'declares',
            
            # Industry and business terms
            'industry', 'market', 'trade', 'export', 'import',
            'technology', 'innovation', 'sustainability', 'compliance',
            'manufacturing', 'production', 'supply chain', 'logistics',
            'investment', 'funding', 'financing', 'revenue', 'profit',
            'partnership', 'collaboration', 'agreement', 'contract',
            
            # Time-based indicators
            'today', 'yesterday', 'this week', 'this month', 'this year',
            'latest', 'recent', 'new', 'updated', 'breaking',
            
            # Event indicators
            'event', 'conference', 'summit', 'meeting', 'workshop',
            'exhibition', 'fair', 'show', 'presentation', 'seminar'
        ]
        
        has_news_content = any(pattern in title_lower for pattern in news_patterns)
        
        # 4. Check title structure and formatting
        looks_like_headline = (
            len(title) >= 20 and 
            len(title) <= 200 and
            title[0].isupper() and
            not title.isupper() and  # Not all caps
            not title.islower() and  # Not all lowercase
            title.count(' ') >= 3    # At least 4 words
        )
        
        # 5. Check for proper URL structure (should contain article/news identifiers)
        has_news_url_structure = any(pattern in url_lower for pattern in [
            '/article/', '/news/', '/story/', '/post/', '/blog/',
            '/202', '/2024', '/2025',  # Year indicators
            '/jan/', '/feb/', '/mar/', '/apr/', '/may/', '/jun/',
            '/jul/', '/aug/', '/sep/', '/oct/', '/nov/', '/dec/'
        ])
        
        # 6. Final validation
        is_valid = (
            (has_news_content or looks_like_headline) and
            has_news_url_structure and
            not any(char.isdigit() for char in title[:5])  # Title shouldn't start with numbers
        )
        
        if is_valid:
            print(f"      ✅ Valid news link: {title[:50]}...")
        else:
            print(f"      ❌ Skipped: Doesn't meet news link criteria")
            if not has_news_content and not looks_like_headline:
                print(f"         - No news content or headline structure")
            if not has_news_url_structure:
                print(f"         - No news URL structure")
        
        return is_valid

    def _is_rmg_related(self, text: str) -> bool:
        """Check if text is related to RMG industry"""
        if not text:
            return False
        
        rmg_keywords = [
            'rmg', 'textile', 'garment', 'apparel', 'clothing', 'fashion',
            'manufacturing', 'export', 'cotton', 'fabric', 'factory',
            'bangladesh', 'bgmea', 'bkmea', 'trade', 'industry'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in rmg_keywords)

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title from HTML"""
        title_selectors = [
            'h1',
            '.article-title',
            '.post-title',
            '.entry-title',
            '.headline',
            'title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and len(title) > 10:
                    return title
        
        return ""

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract article content from HTML"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            element.decompose()
        
        content_selectors = [
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content',
            'article',
            '.article-body',
            '.post-body',
            '.story-content'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # Get all paragraphs
                paragraphs = element.find_all(['p', 'div'])
                content_parts = []
                
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:  # Filter out short text
                        content_parts.append(text)
                
                if content_parts:
                    return '\n\n'.join(content_parts)
        
        # Fallback: get all paragraphs
        paragraphs = soup.find_all('p')
        content_parts = []
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 20:
                content_parts.append(text)
        
        return '\n\n'.join(content_parts)

    def _extract_date(self, soup: BeautifulSoup) -> datetime:
        """Extract publication date from HTML"""
        date_selectors = [
            '.published-date',
            '.post-date',
            '.article-date',
            '.date',
            'time',
            '.timestamp'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                date_text = element.get_text(strip=True)
                # Try to parse various date formats
                try:
                    # Add more date parsing logic here if needed
                    return datetime.now()
                except:
                    continue
        
        return datetime.now()

    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract author from HTML"""
        author_selectors = [
            '.author',
            '.post-author',
            '.article-author',
            '.byline',
            '.writer'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                author = element.get_text(strip=True)
                if author and len(author) > 2:
                    return author
        
        return ""

    async def _clean_content_with_ai(self, content: str, title: str) -> str:
        """Use AI to clean content only (no summary generation)"""
        print(f"      🤖 Starting AI content cleaning...")
        try:
            prompt = f"""
            Please clean this RMG industry news article content:
            
            Title: {title}
            Raw Content: {content[:3000]}  # Limit to avoid token limits
            
            Please return ONLY the cleaned article content (no JSON, no title, no metadata) in this exact JSON format:
            {{
                "cleaned_content": "Pure article content with proper formatting, no title or metadata"
            }}
            
            Important:
            - Return ONLY the article content in cleaned_content (no title, no JSON wrapper, no metadata)
            - Make the content readable and well-formatted
            - Remove any HTML artifacts or formatting issues
            - Keep all important information and details
            - Do NOT generate any summary, just clean the content
            """
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert content editor specializing in RMG industry news. Clean article content only, no summaries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 2500
            }
            
            print(f"      📡 Making AI API request...")
            response = requests.post(
                self.deepseek_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"      ✅ AI API request successful")
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                
                try:
                    print(f"      🔍 Parsing AI response...")
                    enhanced_data = json.loads(ai_response)
                    cleaned_content = enhanced_data.get("cleaned_content", content)
                    
                    # Ensure content is clean (no JSON artifacts)
                    if cleaned_content.startswith('{') or cleaned_content.startswith('"'):
                        # If AI returned JSON instead of clean content, use original
                        print(f"      ⚠️  AI returned JSON artifacts, using original content")
                        cleaned_content = content
                    
                    print(f"      ✅ AI content cleaning completed")
                    return cleaned_content
                except json.JSONDecodeError:
                    print(f"      ⚠️  Failed to parse AI JSON response, using original content")
                    return content
            else:
                print(f"      ❌ AI API request failed: {response.status_code}")
                return content
                
        except Exception as e:
            print(f"      💥 AI content cleaning failed: {str(e)}")
            logger.error(f"AI content cleaning failed: {str(e)}")
            return content

# Singleton instance
agno_service = AgnoService() 