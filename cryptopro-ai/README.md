# CryptoPro AI - Professional Cryptocurrency ATH Recovery Prediction Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

## 🚀 Overview

CryptoPro AI is a **production-grade, enterprise-level** platform for analyzing, ranking, and predicting cryptocurrency returns to their All-Time High (ATH). Built with cutting-edge technology and professional architecture, it provides institutional-quality analytics for the top 1000 cryptocurrencies.

### Key Features

- **ATH Recovery Scanner**: Real-time analysis of 1000+ cryptocurrencies distance from ATH
- **AI Prediction Engine**: Advanced ensemble models combining ML, Deep Learning, and statistical analysis
- **Technical Analysis Suite**: 20+ professional indicators (RSI, MACD, Bollinger Bands, ADX, etc.)
- **On-Chain Analytics**: Whale detection, smart money movement, holder distribution
- **Sentiment Analysis**: Social media sentiment from Twitter, Reddit, Telegram, News
- **Moonshot Scanner**: AI-powered identification of high-probability recovery candidates
- **Real-Time Updates**: WebSocket-based live price updates and score changes
- **Backtesting Engine**: Historical validation of AI predictions
- **Professional Dashboard**: TradingView-style charts and analytics

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js 14)                   │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │  Dashboard  │   Coins     │ AI Predict  │  Moonshot   │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ REST API / WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (FastAPI)                     │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │   Auth      │   Coins     │    AI       │  Dashboard  │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  PostgreSQL   │  │    Redis      │  │   Celery      │
│  + TimescaleDB│  │   (Cache)     │  │   Workers     │
└───────────────┘  └───────────────┘  └───────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  External Data Sources                       │
│  CoinGecko │ Binance │ CoinMarketCap │ Glassnode │ Santiment│
└─────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

### Required Software

- **Docker Desktop** (Windows/Mac) or **Docker + Docker Compose** (Linux)
- **Node.js 18+** (for local development)
- **Python 3.11+** (for local development)
- **Git**

### API Keys (Optional but Recommended)

For production use with real data:

- **CoinGecko API** (Free tier available)
- **CoinMarketCap API** (Free tier available)
- **Binance API** (Free)
- **Glassnode API** (Paid, for on-chain data)
- **Santiment API** (Paid, for sentiment data)
- **Alternative.me** (Free, Fear & Greed Index)

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd cryptopro-ai

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

**Access Points:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Redis Insight**: http://localhost:8081

### Option 2: Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Start development server
npm run dev
```

## 📁 Project Structure

```
cryptopro-ai/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/endpoints/   # API Route Handlers
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── coins.py        # Coin management
│   │   │   ├── ai_predictions.py # AI predictions
│   │   │   ├── dashboard.py    # Dashboard data
│   │   │   ├── watchlist.py    # User watchlists
│   │   │   └── alerts.py       # Alert management
│   │   ├── core/               # Core Configuration
│   │   │   ├── config.py       # App settings
│   │   │   ├── database.py     # DB connections
│   │   │   ├── security.py     # JWT, password hashing
│   │   │   └── celery_app.py   # Celery configuration
│   │   ├── db/                 # Database Layer
│   │   │   ├── base.py         # Base model
│   │   │   └── session.py      # DB sessions
│   │   ├── models/             # SQLAlchemy Models
│   │   │   ├── user.py         # User model
│   │   │   ├── coin.py         # Coin & PriceData models
│   │   │   ├── ai_prediction.py # AI prediction models
│   │   │   ├── watchlist.py    # Watchlist model
│   │   │   └── alert.py        # Alert model
│   │   ├── schemas/            # Pydantic Schemas
│   │   │   ├── user.py         # User schemas
│   │   │   ├── coin.py         # Coin schemas
│   │   │   ├── ai_prediction.py # AI schemas
│   │   │   └── ...
│   │   ├── services/           # Business Logic
│   │   │   ├── coin_data_service.py # External API integration
│   │   │   ├── technical_analysis.py # Technical indicators
│   │   │   ├── ai_engine.py    # AI prediction engine
│   │   │   ├── sentiment_analysis.py # Sentiment analysis
│   │   │   └── onchain_analysis.py # On-chain metrics
│   │   ├── workers/            # Celery Tasks
│   │   │   ├── price_updater.py # Price update tasks
│   │   │   ├── ai_calculator.py # AI calculation tasks
│   │   │   └── alert_checker.py # Alert checking tasks
│   │   └── main.py             # FastAPI application
│   ├── alembic/                # Database Migrations
│   ├── tests/                  # Backend Tests
│   ├── requirements.txt        # Python Dependencies
│   ├── Dockerfile              # Backend Docker Image
│   └── .env.example            # Environment Template
│
├── frontend/                   # Next.js Frontend
│   ├── src/
│   │   ├── app/                # App Router Pages
│   │   │   ├── page.tsx        # Homepage
│   │   │   ├── dashboard/      # Dashboard page
│   │   │   ├── coins/          # Coins list
│   │   │   ├── ai-predictions/ # AI predictions
│   │   │   ├── moonshot/       # Moonshot scanner
│   │   │   ├── watchlist/      # User watchlist
│   │   │   └── alerts/         # Alert management
│   │   ├── components/         # React Components
│   │   │   ├── ui/             # Base UI components
│   │   │   ├── charts/         # TradingView charts
│   │   │   ├── layout/         # Layout components
│   │   │   ├── coins/          # Coin-related components
│   │   │   └── ai/             # AI components
│   │   ├── lib/                # Utilities
│   │   │   ├── api.ts          # API client
│   │   │   ├── utils.ts        # Helper functions
│   │   │   └── websocket.ts    # WebSocket client
│   │   ├── hooks/              # Custom React Hooks
│   │   ├── stores/             # Zustand Stores
│   │   ├── types/              # TypeScript Types
│   │   └── styles/             # Global Styles
│   ├── public/                 # Static Assets
│   ├── package.json            # Node Dependencies
│   ├── tailwind.config.js      # Tailwind Configuration
│   ├── tsconfig.json           # TypeScript Configuration
│   ├── Dockerfile              # Frontend Docker Image
│   └── .env.local.example      # Environment Template
│
├── scripts/                    # Utility Scripts
│   ├── seed_data.py            # Database seeding
│   ├── backtest.py             # Backtesting script
│   └── deploy.sh               # Deployment script
│
├── tests/                      # Integration Tests
│   ├── backend/                # Backend tests
│   └── frontend/               # Frontend tests
│
├── docs/                       # Documentation
│   ├── api.md                  # API Documentation
│   ├── architecture.md         # Architecture Details
│   └── deployment.md           # Deployment Guide
│
├── docker-compose.yml          # Docker Compose Configuration
├── .gitignore                  # Git Ignore Rules
└── README.md                   # This File
```

## 🔧 Configuration

### Backend Environment Variables

Create `backend/.env` based on `.env.example`:

```env
# Application
APP_NAME=CryptoPro AI
DEBUG=False
SECRET_KEY=your-super-secret-key-change-in-production
API_PREFIX=/api/v1

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/cryptopro
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# JWT Authentication
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# External APIs
COINGECKO_API_KEY=your-coingecko-key
COINMARKETCAP_API_KEY=your-cmc-key
BINANCE_API_KEY=your-binance-key
GLASSNODE_API_KEY=your-glassnode-key
SANTIMENT_API_KEY=your-santiment-key

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Frontend Environment Variables

Create `frontend/.env.local` based on `.env.local.example`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_APP_NAME=CryptoPro AI
```

## 📊 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Logout user |

### Coins

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/coins` | List all coins |
| GET | `/api/v1/coins/{coin_id}` | Get coin details |
| GET | `/api/v1/coins/ath/distance` | Sort by ATH distance |
| GET | `/api/v1/coins/top/{count}` | Get top N coins |
| GET | `/api/v1/coins/search` | Search coins |

### AI Predictions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/ai/predictions` | Get all predictions |
| GET | `/api/v1/ai/prediction/{coin_id}` | Get prediction for coin |
| GET | `/api/v1/ai/moonshot` | Get moonshot candidates |
| GET | `/api/v1/ai/scores/high` | Get high score predictions |
| POST | `/api/v1/ai/recalculate` | Recalculate all scores |

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/dashboard/overview` | Market overview |
| GET | `/api/v1/dashboard/stats` | Market statistics |
| GET | `/api/v1/dashboard/top-ai-picks` | Top AI picks |
| GET | `/api/v1/dashboard/ath-opportunities` | ATH opportunities |

### Watchlist

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/watchlist` | Get user watchlist |
| POST | `/api/v1/watchlist/add` | Add coin to watchlist |
| DELETE | `/api/v1/watchlist/remove/{coin_id}` | Remove from watchlist |

### Alerts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/alerts` | Get user alerts |
| POST | `/api/v1/alerts/create` | Create new alert |
| PUT | `/api/v1/alerts/{alert_id}` | Update alert |
| DELETE | `/api/v1/alerts/{alert_id}` | Delete alert |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `/ws/prices` | Real-time price updates |
| `/ws/scores` | Real-time AI score updates |
| `/ws/alerts` | Real-time alert notifications |

## 🤖 AI Engine

### Technical Indicators (20+)

- **Trend Indicators**: SMA, EMA, VWAP, SuperTrend
- **Momentum Indicators**: RSI, MACD, Stochastic, ADX, CCI
- **Volatility Indicators**: Bollinger Bands, ATR, Keltner Channels
- **Volume Indicators**: Volume Profile, OBV, MFI
- **Support/Resistance**: Pivot Points, Fibonacci Levels
- **Market Structure**: Higher Highs/Lower Lows detection
- **Smart Money Concepts**: Order Blocks, Fair Value Gaps

### AI Scoring Model

```
Final Score = 
  30% × Technical Analysis +
  25% × Fundamental Analysis +
  20% × On-Chain Metrics +
  15% × Market Sentiment +
  10% × Historical Patterns
```

### Machine Learning Models

- **XGBoost**: Feature-based scoring
- **Random Forest**: Classification (recovery probability)
- **LightGBM**: Fast gradient boosting
- **LSTM**: Time series prediction
- **Transformer**: Market behavior analysis
- **Bayesian Model**: Probability estimation
- **Monte Carlo Simulation**: Risk assessment

### Prediction Outputs

For each cryptocurrency:

- **AI Recovery Score** (0-100)
- **Recovery Probability** (%)
- **Estimated Time to ATH** (months)
- **Risk Level** (Low/Medium/High/Very High)
- **Key Factors** (bullish/bearish signals)
- **Confidence Interval**

## 🧪 Testing

### Run Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

### Run Frontend Tests

```bash
cd frontend
npm test
```

### Run Integration Tests

```bash
docker compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📈 Monitoring & Logging

### Health Checks

- `GET /health` - Basic health check
- `GET /health/ready` - Readiness check (includes DB)
- `GET /health/live` - Liveness check

### Logging

All services use structured JSON logging with correlation IDs for distributed tracing.

### Metrics

Prometheus metrics exposed at `/metrics` endpoint.

## 🚢 Deployment

### Production Docker Compose

```bash
docker compose -f docker-compose.prod.yml up -d
```

### Kubernetes

See `k8s/` directory for Kubernetes manifests.

### Environment-Specific Configurations

- **Development**: `docker-compose.yml`
- **Staging**: `docker-compose.staging.yml`
- **Production**: `docker-compose.prod.yml`

## 🔒 Security

- JWT-based authentication with refresh tokens
- Password hashing using bcrypt
- Rate limiting on all endpoints
- CORS configuration
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (React default)
- HTTPS in production
- Secret management via environment variables

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This platform is for **educational and research purposes only**. It does not constitute financial advice. Always do your own research before making investment decisions. Past performance does not guarantee future results.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) first.

## 📞 Support

- **Documentation**: https://docs.cryptopro.ai
- **Issues**: https://github.com/cryptopro-ai/issues
- **Discord**: https://discord.gg/cryptopro-ai
- **Twitter**: @CryptoProAI

---

Built with ❤️ by the CryptoPro AI Team
