'use client'

import { useState, useEffect } from 'react'
import { api, NewsArticle, NewsSource, SourcesResponse } from './api'

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('')
  const [newsArticles, setNewsArticles] = useState<NewsArticle[]>([])
  const [sources, setSources] = useState<{ [key: string]: NewsSource }>({})
  const [selectedSource, setSelectedSource] = useState<string>('all')
  const [loading, setLoading] = useState(true)
  const [fetchingNews, setFetchingNews] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalArticles, setTotalArticles] = useState(0)
  const articlesPerPage = 10

  // Fetch initial data
  useEffect(() => {
    fetchInitialData()
  }, [])

  const fetchInitialData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // First check if backend is available
      const isBackendHealthy = await api.healthCheck()
      if (!isBackendHealthy) {
        setError('Backend server is not responding. Please ensure the backend is running on http://localhost:8000')
        setLoading(false)
        return
      }
      
      console.log('Backend is healthy, fetching sources and news...')
      
      // Fetch available sources
      try {
        const sourcesData = await api.getSources()
        setSources(sourcesData.sources)
        console.log('Sources loaded:', Object.keys(sourcesData.sources).length, 'sources')
      } catch (err) {
        console.error('Failed to fetch sources:', err)
        setSources({})
      }
      
      // Don't fetch news on startup - let user fetch when needed
      console.log('Sources loaded, ready to fetch news when needed')
      
    } catch (err) {
      setError('Failed to load data. Please try again.')
      console.error('Error fetching initial data:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchNews = async (query?: string, page: number = 1) => {
    try {
      setLoading(true)
      const newsData = await api.getNews(query, page, articlesPerPage)
      
      // Set articles immediately without AI analysis
      setNewsArticles(newsData.articles)
      setTotalArticles(newsData.total)
      setTotalPages(Math.ceil(newsData.total / articlesPerPage))
      setCurrentPage(page)
      setLoading(false)
      
      // Add AI summaries to articles asynchronously (non-blocking)
      if (newsData.articles.length > 0) {
        console.log('Starting AI analysis for articles...')
        
        // Process AI analysis in background
        const articlesWithAI = await Promise.allSettled(
          newsData.articles.map(async (article) => {
            try {
              // Get AI analysis for the article
              const analysis = await api.analyzeArticle(article.content, article.title)
              return {
                ...article,
                aiSummary: analysis.key_insights,
                marketImpact: analysis.market_impact,
                confidence: analysis.agno_confidence
              }
            } catch (err) {
              console.error('Failed to analyze article:', article.title, err)
              return {
                ...article,
                aiSummary: null,
                marketImpact: null,
                confidence: null
              }
            }
          })
        )
        
        // Update articles with AI analysis results
        const processedArticles = articlesWithAI.map(result => 
          result.status === 'fulfilled' ? result.value : result.reason
        ).filter(article => article && typeof article === 'object')
        
        setNewsArticles(processedArticles)
        console.log('AI analysis completed for articles')
      }
      
    } catch (err) {
      setError('Failed to fetch news. Please try again.')
      console.error('Error fetching news:', err)
      setLoading(false)
    }
  }



  const fetchNewsFromSources = async () => {
    try {
      setFetchingNews(true)
      setError(null)
      
      console.log('Fetching news from all sources...')
      const result = await api.fetchNewsFromSources(15)
      
      console.log('News fetching completed:', result)
      
      // Refresh the news list and reset to first page
      setCurrentPage(1)
      await fetchNewsBySource(selectedSource, 1)
      
      setError(null)
    } catch (err) {
      setError('Failed to fetch news from sources. Please try again.')
      console.error('Error fetching news from sources:', err)
    } finally {
      setFetchingNews(false)
    }
  }

  const fetchNewsBySource = async (sourceId: string, page: number = 1) => {
    try {
      setLoading(true)
      setError(null)
      
      let newsData
      if (sourceId === 'all') {
        newsData = await api.getNews(undefined, page, articlesPerPage)
      } else {
        newsData = await api.getNewsBySource(sourceId, page, articlesPerPage)
      }
      
      setNewsArticles(newsData.articles)
      setTotalArticles(newsData.total)
      setTotalPages(Math.ceil(newsData.total / articlesPerPage))
      setCurrentPage(page)
      console.log(`News loaded for ${sourceId}:`, newsData.articles.length, 'articles')
      
    } catch (err) {
      setError('Failed to fetch news. Please try again.')
      console.error('Error fetching news:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSourceChange = async (sourceId: string) => {
    setSelectedSource(sourceId)
    setCurrentPage(1) // Reset to first page when changing source
    await fetchNewsBySource(sourceId, 1)
  }



  const handleSearch = async () => {
    if (searchQuery.trim()) {
      try {
        setLoading(true)
        setCurrentPage(1) // Reset to first page when searching
        const newsData = await api.getNews(searchQuery, 1, articlesPerPage, selectedSource === 'all' ? undefined : selectedSource)
        setNewsArticles(newsData.articles)
        setTotalArticles(newsData.total)
        setTotalPages(Math.ceil(newsData.total / articlesPerPage))
      } catch (err) {
        setError('Failed to search news. Please try again.')
        console.error('Error searching news:', err)
      } finally {
        setLoading(false)
      }
    } else {
      setCurrentPage(1) // Reset to first page when clearing search
      await fetchNewsBySource(selectedSource, 1)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const handlePageChange = async (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page)
      if (searchQuery.trim()) {
        // If there's a search query, search with pagination
        try {
          setLoading(true)
          const newsData = await api.getNews(searchQuery, page, articlesPerPage, selectedSource === 'all' ? undefined : selectedSource)
          setNewsArticles(newsData.articles)
        } catch (err) {
          setError('Failed to fetch news. Please try again.')
          console.error('Error fetching news:', err)
        } finally {
          setLoading(false)
        }
      } else {
        // Otherwise fetch by source with pagination
        await fetchNewsBySource(selectedSource, page)
      }
    }
  }

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
    
    if (diffInHours < 1) return 'Just now'
    if (diffInHours < 24) return `${diffInHours} hours ago`
    const diffInDays = Math.floor(diffInHours / 24)
    return `${diffInDays} days ago`
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive': return 'text-green-600'
      case 'negative': return 'text-red-600'
      default: return 'text-yellow-600'
    }
  }

  const getSentimentLabel = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive': return 'Positive'
      case 'negative': return 'Negative'
      default: return 'Neutral'
    }
  }

  if (loading && newsArticles.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading RMG News AI...</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <header className="gradient-bg text-white shadow-lg">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div>
                <h1 className="text-2xl font-bold">RMG News AI</h1>
                <p className="text-sm opacity-90">Intelligent Industry Insights</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <p className="text-red-800">{error}</p>
            <button 
              onClick={fetchInitialData}
              className="text-red-600 hover:text-red-800 text-sm font-medium mt-2"
            >
              Try Again
            </button>
          </div>
        )}



        {/* Search */}
        <div className="bg-white rounded-2xl p-6 shadow-md border border-gray-200 mb-12">
          <div className="flex items-center justify-center">
            <div className="flex items-center space-x-3 w-full max-w-md">
              <input
                type="text"
                placeholder="Search news..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
              />
              <button 
                onClick={handleSearch}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm"
              >
                🔍 Search
              </button>
            </div>
          </div>
        </div>

        {/* News Grid */}
        <div className="space-y-6">
          {/* Main News Column */}
          <div className="space-y-6">
            {/* Source Tabs and Fetch Button */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
              <h2 className="text-xl font-bold text-gray-800">Latest Industry News</h2>
              
              <div className="flex items-center gap-3">
                {/* Fetch News Button */}
                <button
                  onClick={fetchNewsFromSources}
                  disabled={fetchingNews}
                  className="bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center space-x-2"
                >
                  <span>📥</span>
                  <span>{fetchingNews ? 'Fetching...' : 'Fetch News'}</span>
                </button>
              </div>
            </div>

            {/* Source Tabs */}
            <div className="flex flex-wrap gap-3 mb-6">
              <button
                onClick={() => handleSourceChange('all')}
                className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 shadow-md hover:shadow-lg transform hover:-translate-y-1 ${
                  selectedSource === 'all'
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg ring-4 ring-blue-200 ring-opacity-50'
                    : 'bg-white text-gray-700 hover:bg-gray-50 border-2 border-gray-200 hover:border-blue-300'
                }`}
              >
                <span className="flex items-center space-x-2">
                  <span>📰</span>
                  <span>All Sources</span>
                  {selectedSource === 'all' && <span className="text-xs">✓</span>}
                </span>
              </button>
              
              {Object.entries(sources).map(([sourceId, source]) => (
                <button
                  key={sourceId}
                  onClick={() => handleSourceChange(sourceId)}
                  className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 shadow-md hover:shadow-lg transform hover:-translate-y-1 ${
                    selectedSource === sourceId
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg ring-4 ring-blue-200 ring-opacity-50'
                      : 'bg-white text-gray-700 hover:bg-gray-50 border-2 border-gray-200 hover:border-blue-300'
                  }`}
                >
                  <span className="flex items-center space-x-2">
                    <span>📰</span>
                    <span>{source.name}</span>
                    {selectedSource === sourceId && <span className="text-xs">✓</span>}
                  </span>
                </button>
              ))}
            </div>
            
            {loading ? (
              <div className="space-y-6">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="bg-white rounded-xl p-6 shadow-md border border-gray-200">
                    <div className="animate-pulse">
                      <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                      <div className="h-6 bg-gray-200 rounded w-full mb-2"></div>
                      <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                      <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : newsArticles.length > 0 ? (
              newsArticles.map((article, index) => (
                <div key={article.id} className="news-card bg-white rounded-xl p-6 shadow-md border border-gray-200">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-2">
                      <span className="text-gray-600 text-sm">
                        {sources[article.source]?.name || article.source} • {formatTimeAgo(article.published_at)}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      {article.is_processed && (
                        <span className="text-gray-400 text-sm">🤖 AI Summarized</span>
                      )}
                      <span className={`text-xs px-2 py-1 rounded ${
                        sources[article.source] ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
                      }`}>
                        {sources[article.source]?.name || 'Unknown Source'}
                      </span>
                    </div>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">{article.title}</h3>
                  <div className="bg-gray-50 rounded-lg p-4 mb-4">
                    <div className="text-gray-700 leading-relaxed whitespace-pre-wrap text-sm">
                      {article.content}
                    </div>
                  </div>

                  
                  {article.ai_summary && (
                    <div className="bg-blue-50 p-4 rounded-lg mb-4">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="text-blue-600">🧠</span>
                        <span className="text-blue-800 font-medium text-sm">AI Summary</span>
                        {article.confidence_score && (
                          <span className="text-blue-600 text-xs bg-blue-100 px-2 py-1 rounded">
                            {Math.round(article.confidence_score * 100)}% confidence
                          </span>
                        )}
                      </div>
                      <p className="text-blue-800 text-sm">{article.ai_summary}</p>
                      {article.market_impact && (
                        <div className="mt-2 pt-2 border-t border-blue-200">
                          <span className="text-blue-700 text-xs font-medium">Market Impact: </span>
                          <span className="text-blue-600 text-xs capitalize">{article.market_impact}</span>
                        </div>
                      )}
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>{new Date(article.published_at).toLocaleDateString()}</span>
                    </div>
                    <a 
                      href={article.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center space-x-1"
                    >
                      <span>Read Original Article</span>
                      <span>→</span>
                    </a>
                  </div>
                </div>
              ))
            ) : (
              <div className="bg-white rounded-xl p-6 shadow-md border border-gray-200 text-center">
                <p className="text-gray-600">
                  {selectedSource === 'all' 
                    ? 'No news articles found. Click "Fetch News from Sources" to load articles.'
                    : `No news articles found from ${sources[selectedSource]?.name || selectedSource}. Click "Fetch News from Sources" to load articles.`
                  }
                </p>
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center space-x-3 mt-8">
                {/* Previous button */}
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="px-4 py-2 text-sm font-semibold text-gray-500 bg-white border-2 border-gray-200 rounded-lg hover:bg-gray-50 hover:border-blue-300 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-sm hover:shadow-md"
                >
                  ← Previous
                </button>

                {/* Page numbers */}
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum
                  if (totalPages <= 5) {
                    pageNum = i + 1
                  } else if (currentPage <= 3) {
                    pageNum = i + 1
                  } else if (currentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + i
                  } else {
                    pageNum = currentPage - 2 + i
                  }

                  return (
                    <button
                      key={pageNum}
                      onClick={() => handlePageChange(pageNum)}
                      className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-300 shadow-sm hover:shadow-md ${
                        currentPage === pageNum
                          ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg ring-4 ring-blue-200 ring-opacity-50 transform scale-110'
                          : 'text-gray-700 bg-white border-2 border-gray-200 hover:bg-gray-50 hover:border-blue-300 hover:scale-105'
                      }`}
                    >
                      <span className="flex items-center space-x-1">
                        <span>{pageNum}</span>
                        {currentPage === pageNum && <span className="text-xs">●</span>}
                      </span>
                    </button>
                  )
                })}

                {/* Next button */}
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 text-sm font-semibold text-gray-500 bg-white border-2 border-gray-200 rounded-lg hover:bg-gray-50 hover:border-blue-300 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-sm hover:shadow-md"
                >
                  Next →
                </button>
              </div>
            )}

            {/* Page info */}
            {totalArticles > 0 && (
              <div className="text-center mt-6">
                <div className="inline-flex items-center space-x-3 bg-gradient-to-r from-blue-50 to-purple-50 px-6 py-3 rounded-xl border border-blue-200 shadow-sm">
                  <span className="text-blue-600 font-semibold">📊</span>
                  <span className="text-gray-700 font-medium">
                    Page <span className="text-blue-600 font-bold">{currentPage}</span> of <span className="text-blue-600 font-bold">{totalPages}</span>
                  </span>
                  <span className="text-gray-500">•</span>
                  <span className="text-gray-700 font-medium">
                    Showing {((currentPage - 1) * articlesPerPage) + 1} to {Math.min(currentPage * articlesPerPage, totalArticles)} of {totalArticles} articles
                  </span>
                </div>
              </div>
            )}
          </div>


        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white mt-20">
        <div className="container mx-auto px-6 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">RMG News AI</h3>
              <p className="text-gray-400 text-sm">Powered by AGiXT • Real-time Industry Intelligence</p>
            </div>
            <div className="flex items-center space-x-6">
              <span className="text-gray-400 text-sm">
                Last Updated: Just now
              </span>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-green-400 text-sm">Live</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
} 