# RMG News AI Agent

A sophisticated AI-powered news aggregation and analysis platform specifically designed for the Ready-Made Garment (RMG) industry. This application provides real-time market intelligence, sentiment analysis, and industry insights using advanced AI technology.

## 🚀 Features

- **AI-Powered News Analysis**: Real-time news processing and intelligent insights using Agno
- **Market Intelligence Dashboard**: Comprehensive overview of industry trends and metrics
- **Sentiment Analysis**: AI-driven market sentiment tracking across different sectors
- **Trending Topics**: Real-time identification and tracking of industry hot topics
- **Smart Filtering**: Advanced search and category-based news filtering
- **Interactive Reports**: Generate comprehensive industry reports on demand

## 🛠️ Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **Chart.js** - Interactive charts and data visualization
- **React Hook Form** - Form handling and validation

### Backend
- **FastAPI** - High-performance Python web framework
- **Python 3.11+** - Modern Python with async support
- **Pydantic** - Data validation and serialization
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Primary database
- **Redis** - Caching and session management

### AI & Data Processing
- **Agno** - AI framework for news analysis and insights
- **Pandas** - Data manipulation and analysis

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL
- Redis

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd news-agent
   ```

2. **Start with Docker (Recommended)**
   ```bash
   docker-compose up -d
   ```

3. **Manual Setup**

   **Backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

   **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Environment Configuration**
   ```bash
   # Copy environment files
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env.local
   ```

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
DATABASE_URL=postgresql://user:password@localhost/rmg_news
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your_openai_key
NEWS_API_KEY=your_news_api_key
AGNO_API_URL=http://localhost:8001
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AGNO_URL=http://localhost:8001
```

## 📊 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## 🚀 Deployment

### Production Deployment

1. **Build Docker images**
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Individual Service Deployment

- **Frontend**: Deploy to Vercel with automatic deployments from main branch
- **Backend**: Deploy to Railway/Render with environment variables configured
- **Database**: Use managed PostgreSQL service (Supabase, Railway, etc.)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Agno** for AI framework and insights
- **Tailwind CSS** for the beautiful UI components
- **FastAPI** for the high-performance backend
- **Next.js** for the modern React framework

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the documentation in the `/docs` folder

---

**Built with ❤️ for the RMG Industry**
