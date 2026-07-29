# AI Crypto ATH Recovery Prediction Platform

A professional FinTech platform for analyzing, ranking, and predicting cryptocurrency behavior using advanced AI models.

## 🎯 Project Overview

This platform scans the top 1000 cryptocurrencies, analyzes their distance from All-Time High (ATH), and uses ensemble AI models to predict recovery probability.

## 🏗 Architecture

```
crypto-ai-platform/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # REST API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database & ML models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Helper functions
│   └── tests/              # Unit & integration tests
├── frontend/               # Next.js React frontend
│   └── src/
│       ├── app/           # Next.js pages
│       ├── components/    # Reusable UI components
│       ├── hooks/         # Custom React hooks
│       ├── lib/           # Utilities & API clients
│       └── stores/        # State management
├── docker/                # Docker configurations
└── scripts/               # Deployment & utility scripts
```

## 🚀 Features

### 1. ATH Recovery Scanner
- Real-time scanning of top 1000 cryptocurrencies
- Distance from ATH calculation
- Required growth multiplier
- Market data integration

### 2. AI Prediction Engine
- **Technical Analysis**: RSI, MACD, EMA, SMA, Bollinger Bands, ATR, SuperTrend, VWAP
- **Fundamental Analysis**: Market Cap, TVL, Developer Activity, GitHub Stats
- **On-chain Analysis**: Whale Activity, Exchange Flows, Holder Distribution
- **Sentiment Analysis**: Social media, News, Google Trends
- **Ensemble ML Models**: XGBoost, Random Forest, LightGBM, LSTM, Transformers

### 3. Moonshot Scanner
- AI-curated list of highest probability ATH recovery candidates
- Multi-factor scoring system
- Risk assessment

### 4. Smart Scoring System
```
Final Score = 
  30% Technical Analysis +
  25% Fundamental Analysis +
  20% On-chain Data +
  15% Market Sentiment +
  10% Historical Pattern
```

## 🛠 Tech Stack

### Frontend
- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript
- **Styling**: TailwindCSS + Shadcn UI
- **Charts**: TradingView Lightweight Charts
- **State**: Zustand

### Backend
- **Framework**: Python FastAPI
- **Database**: PostgreSQL + TimescaleDB
- **Cache**: Redis
- **ML**: PyTorch, Scikit-learn, XGBoost, LightGBM
- **Task Queue**: Celery + Redis

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack

## 📊 Data Sources

- CoinGecko API
- CoinMarketCap API
- Binance API
- Glassnode API (On-chain)
- Santiment API (Social sentiment)
- LunarCrush API

## 🎨 Dashboard Pages

1. **Dashboard** - Market overview
2. **ATH Scanner** - Coins sorted by ATH distance
3. **AI Predictions** - ML-powered recovery forecasts
4. **Coin Detail** - Individual coin analysis
5. **Watchlist** - Saved coins
6. **Alerts** - Real-time notifications

## 🔐 Security & Quality

- Clean Architecture
- Environment Variables
- Comprehensive Logging
- Error Handling
- Unit & Integration Tests
- API Documentation (OpenAPI/Swagger)
- Scalable Microservices-ready Design

## 📈 AI Backtesting

Historical simulation to validate model accuracy:
- 1-month prediction accuracy
- 3-month prediction accuracy
- 6-month prediction accuracy

## 🚦 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd crypto-ai-platform
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Environment Variables**
```bash
# Copy .env.example to .env in both backend and frontend
cp .env.example .env
```

5. **Start with Docker Compose**
```bash
docker-compose up -d
```

6. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📝 License

MIT License

## 👥 Contributing

Contributions are welcome! Please read our contributing guidelines first.

---

**Built with ❤️ by AI Development Team**
