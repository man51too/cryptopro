# 🚀 CryptoPro AI - Professional Cryptocurrency ATH Recovery Prediction Platform

## 📋 Overview

**CryptoPro AI** is an institutional-grade platform for analyzing, ranking, and predicting the behavior of the top 1000 cryptocurrencies with a focus on identifying assets with the highest probability of returning to their All-Time High (ATH).

### Key Features

- **Real-time Data Processing**: WebSocket-based live price updates from multiple exchanges
- **Advanced AI Engine**: Ensemble machine learning models (XGBoost, LSTM, Transformers)
- **Multi-Factor Analysis**: Technical, Fundamental, On-chain, and Sentiment analysis
- **Professional Dashboard**: TradingView-grade charts and analytics
- **Scalable Architecture**: Microservices design with Kubernetes support
- **Enterprise Security**: JWT authentication, RBAC, encryption at rest and in transit

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer (Nginx)                   │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Frontend   │    │   Backend    │    │   WebSocket  │
│   (Next.js)  │    │  (FastAPI)   │    │   Server     │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │    Redis     │    │  TimescaleDB │
│  (Primary)   │    │   (Cache)    │    │ (Time-series)│
└──────────────┘    └──────────────┘    └──────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  AI Engine   │    │ Data Ingestion│    │   Message    │
│  (PyTorch)   │    │   Service    │    │   Queue      │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## 🛠 Technology Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.x
- **Styling**: TailwindCSS 3.x + Shadcn UI
- **State Management**: Zustand
- **Charts**: TradingView Lightweight Charts + Recharts
- **Data Fetching**: TanStack Query (React Query)
- **WebSocket**: Socket.io-client

### Backend
- **Framework**: FastAPI 0.109+
- **Language**: Python 3.11+
- **Database ORM**: SQLAlchemy 2.0 + AsyncPG
- **Validation**: Pydantic 2.x
- **Task Queue**: Celery + Redis
- **WebSocket**: FastAPI WebSocket + Socket.io

### Database
- **Primary**: PostgreSQL 15 (ACID transactions)
- **Time-series**: TimescaleDB (historical price data)
- **Cache**: Redis 7 (session, real-time data)
- **Search**: Elasticsearch (optional, for advanced search)

### AI/ML
- **Deep Learning**: PyTorch 2.x
- **Traditional ML**: Scikit-learn, XGBoost, LightGBM
- **Time-series**: Statsmodels, Prophet
- **NLP**: Transformers (Hugging Face) for sentiment analysis

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes (production)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)

---

## 📁 Project Structure

```
crypto-pro-platform/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/
│   │   │   ├── coins.py          # Coin endpoints
│   │   │   ├── ai_predictions.py # AI prediction endpoints
│   │   │   ├── dashboard.py      # Dashboard metrics
│   │   │   ├── users.py          # User management
│   │   │   ├── watchlist.py      # Watchlist operations
│   │   │   └── alerts.py         # Alert system
│   │   ├── core/
│   │   │   ├── config.py         # Configuration management
│   │   │   ├── security.py       # JWT, password hashing
│   │   │   ├── database.py       # DB connections
│   │   │   └── exceptions.py     # Custom exceptions
│   │   ├── db/
│   │   │   ├── base.py           # Base model
│   │   │   ├── session.py        # DB sessions
│   │   │   └── init_db.py        # DB initialization
│   │   ├── models/
│   │   │   ├── coin.py           # Coin & CoinData models
│   │   │   ├── ai_prediction.py  # AI prediction models
│   │   │   ├── user.py           # User model
│   │   │   ├── watchlist.py      # Watchlist model
│   │   │   └── alert.py          # Alert model
│   │   ├── schemas/
│   │   │   ├── coin.py           # Pydantic schemas for coins
│   │   │   ├── ai_prediction.py  # Schemas for AI predictions
│   │   │   ├── user.py           # User schemas
│   │   │   └── response.py       # API response schemas
│   │   ├── services/
│   │   │   ├── ai_engine.py      # Main AI prediction engine
│   │   │   ├── technical_analysis.py # Technical indicators
│   │   │   ├── fundamental_analysis.py # Fundamental metrics
│   │   │   ├── onchain_analysis.py # On-chain data processing
│   │   │   ├── sentiment_analysis.py # Social sentiment
│   │   │   ├── coin_data_service.py # External API integration
│   │   │   ├── price_service.py  # Real-time price handling
│   │   │   └── notification_service.py # Alerts & notifications
│   │   ├── utils/
│   │   │   ├── helpers.py        # Utility functions
│   │   │   ├── logger.py         # Logging configuration
│   │   │   └── validators.py     # Input validation
│   │   └── main.py               # FastAPI application entry
│   ├── tests/
│   │   ├── test_api.py           # API endpoint tests
│   │   ├── test_ai_engine.py     # AI engine tests
│   │   └── test_services.py      # Service layer tests
│   ├── scripts/
│   │   ├── seed_data.py          # Database seeding
│   │   └── backtest.py           # Backtesting script
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/        # Main dashboard
│   │   │   ├── scanner/          # ATH Recovery Scanner
│   │   │   ├── ai-prediction/    # AI Predictions page
│   │   │   ├── coin/[id]/        # Individual coin pages
│   │   │   ├── layout.tsx        # Root layout
│   │   │   └── page.tsx          # Home page
│   │   ├── components/
│   │   │   ├── ui/               # Reusable UI components
│   │   │   ├── charts/           # Chart components
│   │   │   └── tables/           # Data tables
│   │   ├── lib/
│   │   │   ├── api.ts            # API client
│   │   │   ├── websocket.ts      # WebSocket client
│   │   │   └── utils.ts          # Utility functions
│   │   ├── hooks/                # Custom React hooks
│   │   ├── stores/               # Zustand stores
│   │   └── styles/
│   │       └── globals.css       # Global styles
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── .env.local.example
│
├── docker/
│   ├── nginx.conf                # Nginx configuration
│   └── prometheus.yml            # Monitoring config
│
├── docs/
│   ├── API.md                    # API documentation
│   ├── ARCHITECTURE.md           # Architecture details
│   └── DEPLOYMENT.md             # Deployment guide
│
├── docker-compose.yml            # Local development
├── docker-compose.prod.yml       # Production setup
├── k8s/                          # Kubernetes manifests
├── README.md                     # This file
└── .gitignore
```

---

## 🔧 Installation & Setup

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- API Keys:
  - CoinGecko Pro / CoinMarketCap
  - Binance API
  - Glassnode (On-chain)
  - Santiment / LunarCrush (Sentiment)

### Quick Start (Docker Compose)

```bash
# Clone repository
git clone <repository-url>
cd crypto-pro-platform

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# Edit environment files with your API keys

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access services:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
# WebSocket: ws://localhost:8000/ws
```

### Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python -m app.db.init_db

# Run migrations (if using Alembic)
alembic upgrade head

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev

# Build for production
npm run build
npm start
```

---

## 📊 Core Modules

### 1. ATH Recovery Scanner

Scans top 1000 cryptocurrencies and calculates:
- Current price vs ATH
- Percentage distance from ATH
- Required growth multiplier
- Time since ATH

**Endpoint**: `GET /api/v1/coins/ath/distance`

### 2. AI Prediction Engine

Multi-factor scoring system:

```
Final Score = 
  30% Technical Analysis (RSI, MACD, EMA, Volume, etc.)
+ 25% Fundamental Analysis (Market Cap, TVL, Dev Activity)
+ 20% On-chain Metrics (Whale Activity, Holder Growth)
+ 15% Market Sentiment (Social Media, News)
+ 10% Historical Patterns (Previous ATH recovery times)
```

**Models Used**:
- XGBoost for feature importance
- LSTM for time-series prediction
- Transformer for market regime detection
- Monte Carlo simulation for probability estimation

**Endpoint**: `GET /api/v1/ai/predictions`

### 3. Moonshot Scanner

Identifies top candidates for ATH recovery based on:
- AI Score > 75
- Reasonable distance from ATH (< 80%)
- Increasing volume trend
- Positive sentiment shift
- Whale accumulation patterns

**Endpoint**: `GET /api/v1/ai/moonshot`

### 4. Real-time Dashboard

Live updates via WebSocket:
- Price changes
- AI score updates
- Alert triggers
- Market overview statistics

**WebSocket Endpoint**: `ws://localhost:8000/ws/market`

---

## 🔐 Security Features

- **Authentication**: JWT-based with refresh tokens
- **Authorization**: Role-Based Access Control (RBAC)
- **Encryption**: AES-256 for sensitive data at rest
- **Rate Limiting**: Per-user and per-IP limits
- **CORS**: Configured for specific origins
- **Input Validation**: Pydantic schemas for all inputs
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy
- **XSS Protection**: Content Security Policy headers

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
npm run test:e2e  # End-to-end tests with Playwright
```

---

## 📈 Performance Optimization

- **Database**: Indexes on frequently queried columns, connection pooling
- **Caching**: Redis for API responses, session storage, real-time data
- **Async Operations**: Async/await throughout backend
- **CDN**: Static assets served via CDN in production
- **Load Balancing**: Nginx reverse proxy with multiple backend instances
- **Database Sharding**: Horizontal scaling for high-volume data

---

## 🚀 Deployment

### Production Docker Compose

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/services.yaml
kubectl apply -f k8s/ingress.yaml
```

---

## 📝 API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

See [docs/API.md](./docs/API.md) for detailed endpoint documentation.

---

## ⚠️ Disclaimer

This platform is for **educational and research purposes only**. It does not constitute financial advice. Always conduct your own research before making investment decisions. Past performance does not guarantee future results.

---

## 📄 License

MIT License - see LICENSE file for details.

---

## 👥 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

---

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Email: support@cryptopro.ai
- Discord: [Join our community]
