# 🛡️ DeFi Rug Pull Detector

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)
[![ML Models](https://img.shields.io/badge/ML-XGBoost%20%7C%20LightGBM%20%7C%20CatBoost%20%7C%20TensorFlow-orange.svg)](https://github.com/)
[![Medium](https://img.shields.io/badge/Medium-Technical%20Deep%20Dive-black?style=for-the-badge&logo=medium)](https://medium.com/@tunahankicci/blockchain-g%C3%BCvenli%C4%9Finde-yapay-zeka-defi-rug-pull-tespit-sistemi-mimarisi-615a636865c2)

**Enterprise-grade DeFi güvenlik platformu** - Yatırımcıları dolandırıcılıklara (rug pull, honeypot, scam) karşı koruyan, **Açıklanabilir Yapay Zeka (XAI)** ve **Ensemble ML** ile desteklenen gerçek zamanlı risk analiz sistemi.

> ⚠️ **Disclaimer**: Bu araç sadece bilgilendirme amaçlıdır ve yatırım tavsiyesi değildir. Her zaman kendi araştırmanızı yapın (DYOR).     
> ⚠️ **Geliştirme Notu:** Bu proje **yapay zeka (LLM)** araçları kullanılarak geliştirilmiştir. "vibe coding" yöntemleriyle oluşturulmuştur.
---

## 🎯 Temel Özellikler

### 🔬 6 Modül + 2 Simülatör
| Modül | Açıklama | Risk Faktörleri |
|-------|----------|-----------------|
| **A. Contract Security** | Akıllı kontrat güvenlik analizi | SELFDESTRUCT, DelegateCall, Proxy, Mint, Blacklist |
| **B. Holder Analysis** | Token holder dağılımı | Gini katsayısı, Top 10 concentration, Whale detection |
| **C. Liquidity Pool** | Likidite havuzu durumu | Lock status, Liquidity USD, Price impact |
| **D. Transfer Anomaly** | Anormal transfer tespiti | Mint/Burn patterns, Suspicious transfers |
| **E. Pattern Matching** | Bilinen scam patternleri | Known scams, Bytecode similarity |
| **F. Tokenomics** | Token ekonomisi | Tax rates, Supply manipulation |
| **🎯 Honeypot Simulator** | Gerçek alım-satım simülasyonu | Buy/Sell test, Tax calculation |
| **🐋 Whale Detector AI** | ML-based whale manipülasyon tespiti | Concentration risk, ML prediction |

### 🧠 Açıklanabilir Yapay Zeka (XAI)
**"Neden bu token riskli?"** sorusunu cevaplayabilen ileri seviye açıklama sistemi:
- ✅ **Risk faktörü açıklaması** - Her faktörün detaylı Türkçe açıklaması
- ✅ **Impact breakdown** - Her faktörün toplam riske katkı yüzdesi (%40, %30, vb.)
- ✅ **Severity labeling** - KRİTİK, YÜKSEK, ORTA, DÜŞÜK risk seviyeleri
- ✅ **Confidence scoring** - Açıklama güven skoru (%95'e kadar)
- ✅ **Görselleştirme** - Bar chart ile risk dağılımı

**XAI Örnek Çıktı:**
```
Risk skoru: 85/100 (YÜKSEK)

Neden?
1. Likidite kilitli değil (%40 etki) - KRİTİK
2. Top 10 cüzdan arzın %90'ına sahip (%30 etki) - YÜKSEK
3. Mint fonksiyonu var (%15 etki) - ORTA
```

### 🤖 Ensemble ML Sistemi (4 Model)
| Model | Accuracy | Açıklama |
|-------|----------|----------|
| **XGBoost** | 86.8% | Gradient boosting - En yüksek doğruluk |
| **LightGBM** | 87.2% | Hızlı gradient boosting |
| **CatBoost** | 86.5% | Categorical feature handling |
| **Deep Neural Network** | 84.1% | 4-layer TensorFlow DNN |
| **🎯 Ensemble** | **88.4%** | Weighted voting kombinasyonu |

**40 Feature** otomatik çıkarımı ile risk skorlama.

### 🎯 Honeypot Simulator
Gerçek blockchain üzerinde **simüle alım-satım** yaparak honeypot tuzaklarını tespit eder:
- ✅ **Buy Simulation** - Token satın alınabiliyor mu?
- ✅ **Sell Simulation** - Token satılabiliyor mu?
- ✅ **Tax Calculation** - Gerçek alım/satım vergileri
- ✅ **Gas Estimation** - Transaction maliyetleri
- ✅ **Confidence Scoring** - high/medium/low

**Verdicts**: SAFE, HONEYPOT, HIGH_TAX, SUSPICIOUS, UNKNOWN

### 🐋 Whale Detector AI
**Random Forest ML modeli** ile whale manipülasyon riski analizi:
- ✅ **ML Prediction** - 73/100 risk skoru
- ✅ **Confidence** - 85% güven seviyesi
- ✅ **Holder Metrics** - Top holder %, Gini coefficient
- ✅ **Verdict** - SAFE, MODERATE_WHALE_RISK, HIGH_WHALE_RISK, EXTREME_WHALE_RISK

### ⚡ Ek Özellikler
- 🔄 **Real-time Analysis** - 20-30 saniyede kapsamlı analiz
- 📊 **Multi-chain Support** - Ethereum, BSC, Polygon
- 🎨 **Modern UI** - Responsive React + Tailwind CSS
- 📈 **Data Visualization** - Radar chart, Bar chart, Pie chart
- 🚀 **Async Architecture** - Non-blocking I/O, yüksek performans
- 📝 **Comprehensive Logging** - Detaylı analiz kayıtları
- 🌐 **RESTful API** - FastAPI + Swagger documentation

## 🏗️ Teknoloji Stack

### Backend
- **FastAPI 0.109** - Modern async REST API framework
- **Web3.py 6.15** - Ethereum blockchain etkileşimi
- **Etherscan API V2** - On-chain data ve verified contract bilgileri
- **Chainlink Price Feeds** - Gerçek zamanlı fiyat dataları
- **Uvicorn** - ASGI server with auto-reload

### Machine Learning & AI
- **TensorFlow 2.15** & **Keras 2.15** - Deep learning framework
- **XGBoost 2.0.3** - Gradient boosting classifier
- **LightGBM 4.2.0** - Microsoft'un hafif GB implementasyonu
- **CatBoost 1.2.2** - Yandex'in categorical boosting library
- **SHAP 0.44** - Explainable AI (XAI) library
- **Scikit-learn 1.4.0** - Feature engineering ve metrics
- **NumPy & Pandas** - Data manipulation
- **Joblib** - Model serialization

### Frontend
- **React 18** - Component-based UI framework
- **Vite 5** - Lightning-fast build tool ve HMR
- **Tailwind CSS 3** - Utility-first CSS framework
- **Recharts** - Interactive data visualization
- **Axios** - HTTP client (120s timeout)
- **React Router** - Client-side routing
- **Lucide React** - Modern icon library

### Blockchain Infrastructure
- **Uniswap V2/V3** - DEX integration
- **PancakeSwap** - BSC DEX integration
- **Infura/Alchemy** - Ethereum node providers
- **Etherscan/BSCScan/PolygonScan** - Blockchain explorers

## 📦 Kurulum

### Gereksinimler
- **Python 3.10+** (3.10 önerilir)
- **Node.js 18+** & **npm**
- **Ethereum Node** veya **Infura/Alchemy API Key**
- **Etherscan API Key**
- Git

### 1️⃣ Projeyi Klonlayın

```bash
git clone https://github.com/TunahanKicci/defi-rugpull-detector.git
cd defi-rugpull-detector
```

### 2️⃣ Backend Kurulumu

```bash
cd backend

# Virtual environment oluşturun
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Çevre değişkenlerini ayarlayın
cp .env.example .env
# .env dosyasını düzenleyin:
# - ETHEREUM_RPC_URL
# - ETHERSCAN_API_KEY
# - BSC_RPC_URL (opsiyonel)
# - POLYGON_RPC_URL (opsiyonel)

# ML modellerini train edin (opsiyonel - pre-trained modeller dahil)
python train_models.py --generate --samples 1000

# Backend'i başlatın
python main.py
```

Backend `http://localhost:8000` adresinde çalışacak.

### 3️⃣ Frontend Kurulumu

```bash
cd frontend

# Bağımlılıkları yükleyin
npm install

# Çevre değişkenlerini ayarlayın (gerekirse)
cp .env.example .env

# Development server'ı başlatın
npm run dev
```

Frontend `http://localhost:5173` adresinde çalışacak.

### 4️⃣ Model Eğitimi (Opsiyonel)

Kendi verilerinizle model eğitmek için:

```bash
cd backend

# Sentetik data ile eğitim
python train_models.py --generate --samples 1000

# Kendi CSV dosyanızla eğitim (40 feature gerekli)
python train_models.py --data path/to/your/data.csv
```

Eğitim sonrası modeller `backend/data/models/` klasörüne kaydedilir.

## 🐋 Docker ile Kurulum (Önerilir)
> 💡 **Altyapı Notu:**
> Bu proje, geliştirme ortamında hızlı kurulum için **Docker Compose** kullanmaktadır.
>

Docker kullanan yöntem, tüm bağımlılıkları otomatik olarak kurar ve kurulum sorunlarını ortadan kaldırır.

### Gereksinimler
- **Docker Desktop** yüklü olmalı
- **Docker Compose** (Docker Desktop ile birlikte gelir)

### Hızlı Başlangıç

**Windows:**
```powershell
docker-start.bat
```

**Terminal (herhangi platform):**
```bash
docker-compose up -d
```

### Erişim Noktaları

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

**Production (Render + Custom Domain)**
- **Live Site**: https://tunahankicci.me/
- **Backend (Render)**: otomatik olarak `rugpull-detector-backend` host'una yönlenir (Render servis bağlantısı sayesinde `VITE_API_BASE_URL` build sırasında doldurulur).
- **Region/Plan**: Frankfurt, free tier.

### Yararlı Docker Commands

```bash
# Servisleri başlat
docker-compose up -d

# Logları canlı izle (tüm servisler)
docker-compose logs -f

# Belirli servisin logları
docker-compose logs -f backend
docker-compose logs -f frontend

# Servisleri durdur
docker-compose down
```

**Prod deployment:** `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d`

**Detaylı bilgi için**: [docs/DOCKER.md](docs/DOCKER.md)

## �🚀 Kullanım

### Temel Kullanım

1. **Backend ve Frontend'i başlatın**
2. **Tarayıcıda `http://localhost:5173` adresini açın**
3. **Token kontrat adresini girin** (örn: `0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84`)
4. **Blockchain seçin** (Ethereum, BSC, Polygon)
5. **"Analyze" butonuna tıklayın**
6. **~20-30 saniye bekleyin** (analiz süresi)
7. **Risk skorunu ve detayları inceleyin**

### Risk Skoru Yorumlama

- **0-20**: 🟢 **LOW RISK** - Güvenli görünüyor
- **21-40**: 🟡 **MEDIUM-LOW RISK** - Dikkatli inceleyin
- **41-60**: 🟠 **MEDIUM RISK** - Detaylı araştırma yapın
- **61-80**: 🔴 **HIGH RISK** - Ciddi risk faktörleri var
- **81-100**: ⛔ **CRITICAL RISK** - Yatırım yapmamanız önerilir

### API Kullanımı

```bash
# Token analizi
curl -X POST "http://localhost:8000/api/analyze/0xTOKEN_ADDRESS?chain=ethereum"

# Health check
curl "http://localhost:8000/health"

# Analysis history
curl "http://localhost:8000/api/history"
```

### Örnek Analiz Sonucu

```json
{
  "address": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
  "chain": "ethereum",
  "risk_score": 31.6,
  "risk_level": "LOW",
  "contract_info": {
    "name": "Liquid staked Ether 2.0",
    "symbol": "stETH",
    "decimals": 18,
    "total_supply": 8654004.4
  },
  "modules": {
    "contract_security": {
      "risk_score": 30,
      "warnings": ["🚨 CRITICAL: Contract has SELFDESTRUCT capability"]
    },
    "holder_analysis": {
      "risk_score": 10,
      "data": {
        "top_10_percentage": 47.5,
        "gini_coefficient": 0.928,
        "total_holders": 1080
      }
    },
    "liquidity_pool": {
      "risk_score": 5,
      "data": {
        "liquidity_usd": 4327584.03,
        "is_locked": false,
        "price_usd": 3187.28
      }
    }
  },
  "honeypot_simulation": {
    "verdict": "SAFE",
    "data": {
      "buy_simulation": {"success": true, "gas": 139247},
      "sell_simulation": {"success": true, "gas": 250000}
    },
    "confidence": "high"
  },
  "whale_detector": {
    "risk_score": 73.6,
    "confidence": 0.85,
    "verdict": "EXTREME_WHALE_RISK",
    "data": {
      "top_holder_pct": 46.8,
      "gini_coefficient": 0.928
    }
  },
  "risk_explanation": {
    "summary": "Risk skoru: 32/100 (DÜŞÜK)\n\nAna risk faktörleri:\n1. AI tespit: Whale manipülasyonu (85% güven) (%48 etki)\n2. Likidite kilitli değil (%26 etki)\n3. Pattern Eşleştirme (%26 etki)",
    "top_factors": [
      {
        "rank": 1,
        "factor": "AI tespit: Whale manipülasyonu (85% güven)",
        "description": "Whale Dedektörü AI risk faktörü",
        "risk_contribution": 73.0,
        "impact_percentage": 47.7,
        "severity": "YÜKSEK"
      },
      {
        "rank": 2,
        "factor": "Likidite kilitli değil",
        "description": "Likidite havuzu endişe verici",
        "risk_contribution": 40.0,
        "impact_percentage": 26.1,
        "severity": "ORTA"
      }
    ],
    "impact_breakdown": {
      "AI tespit: Whale manipülasyonu (85% güven)": 47.7,
      "Likidite kilitli değil": 26.1,
      "Pattern Eşleştirme": 26.1
    },
    "explanation_confidence": 0.65
  },
  "recommendations": [
    "✅ Lower risk detected, but always DYOR",
    "🔍 Continue monitoring for changes"
  ],
  "analysis_duration_ms": 18434.62,
  "cached": false
}
```

## 📡 API Endpoints

### Analysis
- `POST /api/analyze/{address}` - Token risk analizi
  - Query params: `chain` (ethereum/bsc/polygon), `force_refresh` (bool)
  - Response: Comprehensive risk assessment with ML predictions

### Monitoring
- `GET /api/monitor/{address}` - Real-time monitoring endpoint
  - Query params: `chain`, `interval` (seconds)

### History
- `GET /api/history` - Analiz geçmişi
  - Returns: Last 100 analysis results with timestamps

### Health
- `GET /health` - System health check
  - Returns: API status, version, uptime

### Documentation
- `GET /docs` - Interactive Swagger UI
- `GET /redoc` - ReDoc documentation

## 🏗️ Proje Yapısı

```
defi-rugpull-detector/
├── backend/
│   ├── api/                      # API routes & middleware
│   │   ├── routers/              # FastAPI routers
│   │   │   ├── analysis.py       # Token analysis endpoint
│   │   │   ├── health.py         # Health check
│   │   │   ├── history.py        # Analysis history
│   │   │   └── monitoring.py     # Real-time monitoring
│   │   ├── middleware/           # HTTP middleware
│   │   │   ├── cors.py           # CORS configuration
│   │   │   ├── rate_limiter.py   # Rate limiting
│   │   │   └── error_handler.py  # Global error handling
│   │   └── models/               # Pydantic models
│   │       ├── request.py        # Request schemas
│   │       └── response.py       # Response schemas
│   │
│   ├── modules/                  # Analysis modules (A-K)
│   │   ├── a_contract_security.py    # Module A: Bytecode analysis
│   │   ├── b_holder_analysis.py      # Module B: Holder distribution
│   │   ├── c_liquidity_pool.py       # Module C: Liquidity analysis
│   │   ├── d_transfer_anomaly.py     # Module D: Transfer patterns
│   │   ├── e_pattern_matching.py     # Module E: Scam patterns
│   │   ├── f_tokenomics.py           # Module F: Tokenomics
│   │   ├── h_ml_risk_scorer.py       # Module H: ML ensemble
│   │   ├── i_honeypot_simulator.py   # Honeypot simulation
│   │   ├── k_whale_detector.py       # Whale detector AI
│   │   ├── xai_explainer.py          # XAI explanation system
│   │   └── ml/                       # Machine learning
│   │       ├── ensemble_model.py     # 4-model ensemble
│   │       ├── feature_extractor.py  # 40 feature extraction
│   │       ├── deep_model.py         # TensorFlow DNN
│   │       └── train_whale_model.py  # Whale model trainer
│   │
│   ├── services/                 # Business logic layer
│   │   ├── analysis_orchestrator.py  # Main orchestration
│   │   ├── cache_manager.py          # Redis cache
│   │   ├── websocket_manager.py      # WebSocket support
│   │   └── blockchain/               # Chain integrations
│   │       ├── base_chain.py         # Base blockchain class
│   │       ├── ethereum.py           # Ethereum integration
│   │       ├── bsc.py                # BSC integration
│   │       └── polygon.py            # Polygon integration
│   │
│   ├── config/                   # Configuration
│   │   ├── settings.py           # App settings
│   │   └── chains.py             # Blockchain configs
│   │
│   ├── utils/                    # Utility functions
│   │   ├── logger.py             # Logging setup
│   │   ├── validators.py         # Input validation
│   │   ├── formatters.py         # Data formatting
│   │   └── constants.py          # Global constants
│   │
│   ├── data/
│   │   ├── models/               # Pre-trained ML models
│   │   │   ├── xgboost_model.pkl
│   │   │   ├── lightgbm_model.pkl
│   │   │   ├── catboost_model.pkl
│   │   │   ├── deep_model.h5
│   │   │   ├── whale_detector_rf.pkl
│   │   │   ├── label_encoder.pkl
│   │   │   └── MODEL_PERFORMANCE.md
│   │   ├── scam_database/        # Known scam database
│   │   │   └── known_scams.json
│   │   └── training_data.csv     # Synthetic training data
│   │
│   ├── catboost_info/            # CatBoost training logs
│   │   ├── catboost_training.json
│   │   ├── learn_error.tsv
│   │   ├── time_left.tsv
│   │   └── learn/
│   │
│   ├── logs/                     # Backend application logs
│   │
│   ├── train_models.py           # Model training script
│   ├── check_models.py           # Model validation
│   ├── test_ml.py                # ML testing
│   ├── main.py                   # FastAPI application entry
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Backend container
│   ├── start_backend.bat         # Windows startup script
│   └── start_backend.sh          # Linux/Mac startup script
│
├── frontend/
│   ├── src/
│   │   ├── components/           # React components
│   │   │   └── Layout/
│   │   │       ├── Header.jsx
│   │   │       ├── Footer.jsx
│   │   │       └── Navigation.jsx
│   │   ├── pages/                # Page components
│   │   │   ├── Home.jsx          # Landing page
│   │   │   ├── AnalysisResult.jsx # Main analysis page
│   │   │   ├── History.jsx       # Analysis history
│   │   │   ├── About.jsx         # About page
│   │   │   ├── Monitor.jsx       # Monitoring page
│   │   │   └── NotFound.jsx      # 404 page
│   │   ├── services/             # API clients
│   │   │   ├── api.js            # Axios instance
│   │   │   └── analysisService.js # Analysis API
│   │   ├── styles/               # CSS files
│   │   │   └── index.css         # Global styles + Tailwind
│   │   ├── App.jsx               # Root component
│   │   └── main.jsx              # React entry point
│   │
│   ├── public/                   # Static assets
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js            # Vite configuration
│   ├── tailwind.config.js        # Tailwind CSS config
│   ├── postcss.config.js         # PostCSS config
│   ├── nginx.conf                # Nginx configuration for production
│   ├── Dockerfile                # Frontend container
│   ├── Dockerfile.dev            # Development Dockerfile
│   ├── Dockerfile.prod           # Production Dockerfile
│   ├── start_frontend.bat        # Windows startup script
│   └── start_frontend.sh         # Linux/Mac startup script
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md           # System architecture
│   ├── DOCKER.md                 # Docker deployment guide
│   └── GETTING_STARTED.md        # Quick start guide
│
│
├── tests/                        # Testing & benchmarks
│   ├── performance_reports/      # Performance test results
│   │   ├── deep_analysis_benchmark.md
│   │   ├── infrastructure_benchmark.md
│   │   └── SUMMARY.md
│   └── quality/                  # Code quality reports
│       └── REPORT.md
│
├── scripts/                      # Utility scripts
├── logs/                         # Application logs
├── docker-compose.yml            # Docker orchestration (development)
├── docker-compose.prod.yml       # Docker orchestration (production)
├── render.yaml                   # Render.com deployment config
├── requirements.txt              # Root Python dependencies
├── .gitignore
├── LICENSE
└── README.md                     # This file
```


## 📉 Performans & Kalite Raporları

Proje, endüstri standartlarında güvenilirlik sağlamak için düzenli olarak yük ve statik kod analizi testlerinden geçirilmektedir. (Son Güncelleme: 17 Ocak 2026)

### 🚀 Performans Benchmark Sonuçları
Sistem, yerel geliştirme ortamında (Uvicorn + FastAPI) stres testine tabi tutulmuştur.

| Metrik | Sonuç | Durum | Endüstri Standardı |
|--------|-------|-------|--------------------|
| **Altyapı Yanıt Hızı** | 5-106ms | ✅ Mükemmel | < 100ms |
| **Throughput (Statik)** | 258.42 req/s | ✅ Mükemmel | > 100 req/s |
| **ML Analiz Süresi** | 12-25 sn | ✅ Beklenen | 10-30 sn |
| **ML İşlem Kapasitesi**| 0.08 req/s | ⚠️ Normal | ML yoğun işlem |

> **Not:** ML analiz süresi, blockchain veri toplama ve 4 farklı yapay zeka modelinin (Ensemble) çalıştırılmasını kapsadığı için 12-25 saniye aralığı normal kabul edilmektedir.

### 🛡️ SonarCloud Kalite Analizi
Proje kodu sürekli olarak SonarCloud statik analiz araçları ile taranmaktadır.

| Kategori | Derece | Detay |
|----------|:------:|-------|
| **Güvenlik (Security)** | **A** | 0 Kritik zafiyet (Vulnerability) |
| **Güvenilirlik** | **B** | Exception handling geliştirmeleri sürüyor |
| **Bakım (Maintainability)**| **A** | Düşük teknik borç |
| **Kod Tekrarı** | **%2.1** | Mükemmel modüler yapı (< %5 ideal) |

Detaylı raporlar için `/tests/performance_reports` ve `/tests/quality` dizinlerini inceleyebilirsiniz.

## ☁️ Render Deploy Notları
- Manifest: [render.yaml](render.yaml) (backend root `backend/`, frontend root `frontend/`).
- Backend: `pip install -r requirements.txt && python train_models.py --generate --samples 1000` ile build, `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 --no-access-log` ile start; `APP_ENV=production`, `PYTHON_VERSION=3.10.12` ve `rugpull-detector-cache` Redis servisi bağlı.
- Frontend: `npm install && npm run build`, `dist/` publish path, `VITE_API_BASE_URL` Render'daki backend host'undan otomatik çekilir.
- Redis: `rugpull-detector-cache` free plan, Frankfurt, `allkeys-lru` eviction.
- Custom domain: https://tunahankicci.me/ Render frontend servisine yönlendirildi.

## 🔧 Konfigürasyon

### Backend Environment Variables

```env
# Blockchain RPC URLs
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY
BSC_RPC_URL=https://bsc-dataseed.binance.org/
POLYGON_RPC_URL=https://polygon-rpc.com/

# API Keys
ETHERSCAN_API_KEY=your_etherscan_api_key
BSCSCAN_API_KEY=your_bscscan_api_key
POLYGONSCAN_API_KEY=your_polygonscan_api_key

# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# ML Model Settings
MODEL_DIR=data/models
FEATURE_COUNT=40
ENSEMBLE_WEIGHTS=0.25,0.25,0.25,0.25  # XGB,LGB,Cat,Deep
```

### Frontend Environment Variables

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=120000
```

## 📊 ML Model Details

### Feature Engineering (40 Features)

**Module A - Contract Security (8)**
- has_bytecode, is_verified, has_selfdestruct
- has_delegatecall, is_proxy, has_owner
- is_pausable, contract_risk_score

**Module B - Holder Analysis (5)**
- top_10_concentration, top_holder_pct
- gini_coefficient, unique_holders
- holder_risk_score

**Module C - Liquidity Pool (4)**
- lp_locked, liquidity_usd
- has_pair, liquidity_risk_score

**Module D - Transfer Anomaly (7)**
- mint_count, burn_count
- unique_senders, unique_receivers
- avg_transfer_value, anomaly_score
- transfer_risk_score

**Module E - Pattern Matching (4)**
- is_known_scam, honeypot_pattern
- similarity_score, pattern_risk_score

**Module F - Tokenomics (6)**
- total_supply, has_tax
- buy_tax, sell_tax, total_tax
- tokenomics_risk_score

**Derived Features (6)**
- risk_score_variance, high_risk_modules
- weighted_risk, confidence_avg
- has_critical_flags, liquidity_holder_ratio

### Model Performance

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|-------|----------|-----------|--------|----------|---------|
| XGBoost | 86.8% | 86.6% | 92.4% | 89.4% | 86.4% |
| LightGBM | 87.2% | 86.6% | 92.4% | 89.4% | 86.4% |
| CatBoost | 86.5% | 86.6% | 92.4% | 89.4% | 86.4% |
| Deep NN | 84.1% | 84.0% | 100% | 91.3% | 66.3% |
| **Ensemble** | **88.4%** | **86.6%** | **92.4%** | **89.4%** | **86.4%** |

*Trained on 1000 synthetic samples (840 rug pulls, 160 safe tokens)*

### XAI (Explainable AI) Sistemi

**Risk Explanation Engine** - SHAP-inspired açıklama sistemi:

1. **Risk Factor Extraction**
   - Her modülden spesifik risk faktörleri çıkarımı
   - Honeypot ve Whale detector sonuçlarının entegrasyonu
   - Top 10 risk faktörünün belirlenmesi

2. **Impact Calculation**
   - Her faktörün toplam riske katkı yüzdesinin hesaplanması
   - Risk score normalizasyonu ve impact breakdown
   - Confidence score hesaplama (50%-95%)

3. **Turkish Explanation Generation**
   - 100+ risk faktörü için Türkçe açıklama library
   - Severity labeling (KRİTİK, YÜKSEK, ORTA, DÜŞÜK)
   - Human-readable summary oluşturma

4. **Visualization**
   - Bar chart ile impact breakdown görselleştirme
   - Color-coded severity badges
   - Top 5 faktör detaylı açıklama kartları

**XAI Confidence Levels:**
- High (80%-95%): Çok sayıda belirgin risk faktörü
- Medium (65%-79%): Orta düzeyde risk faktörü
- Low (50%-64%): Az sayıda risk faktörü

### Whale Detector AI

**Random Forest Model** - Whale manipülasyon risk tespiti:
- **Training Data**: 1000+ holder distribution samples
- **Features**: 8 concentration metrics (Gini, top holder %, etc.)
- **Algorithm**: Random Forest Regressor (200 trees, max_depth=12)
- **Output**: Risk score (0-100) + Confidence (0-1)

**Verdicts:**
- SAFE (0-30): Normal dağılım
- MODERATE_WHALE_RISK (31-60): Dikkat gerekli
- HIGH_WHALE_RISK (61-79): Yüksek konsantrasyon
- EXTREME_WHALE_RISK (80-100): Kritik whale riski

### Honeypot Simulator

**Transaction Simulation** - Gerçek blockchain üzerinde:
1. **Buy Test**: Simüle token satın alma (eth_call)
2. **Sell Test**: Simüle token satma (router üzerinden)
3. **Tax Calculation**: Gerçek alım/satım vergi hesabı
4. **Gas Estimation**: Transaction maliyeti tahmini

**Detection Patterns:**
- Transfer lock (cannot sell)
- High sell tax (>50%)
- Blacklist function
- Balance manipulation


## 👥 Yazarlar

- **Tunahan Kıccı** - *Initial work* - [TunahanKicci](https://github.com/TunahanKicci)

## 🙏 Teşekkürler

- **Etherscan** - Comprehensive blockchain data API
- **Chainlink** - Decentralized price feeds
- **FastAPI** - Modern Python web framework
- **TensorFlow** - Machine learning framework
- **Web3.py** - Ethereum library
- **React** & **Vite** - Frontend excellence
- **Open source community** - Amazing tools and libraries

## 📚 Kaynaklar & Dokümantasyon

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs` - Interactive API tester
- **ReDoc**: `http://localhost:8000/redoc` - Alternative documentation
- **OpenAPI Spec**: `http://localhost:8000/openapi.json` - Machine-readable spec

### External APIs
- [Etherscan API v2](https://docs.etherscan.io/) - Ethereum blockchain explorer
- [BSCScan API](https://docs.bscscan.com/) - Binance Smart Chain explorer
- [PolygonScan API](https://docs.polygonscan.com/) - Polygon blockchain explorer
- [Chainlink Price Feeds](https://docs.chain.link/data-feeds/price-feeds) - Decentralized oracles

### Frameworks & Libraries
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Web3.py](https://web3py.readthedocs.io/) - Ethereum library for Python
- [React](https://react.dev/) - JavaScript UI library
- [Vite](https://vitejs.dev/) - Frontend build tool
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS

### Machine Learning
- [XGBoost](https://xgboost.readthedocs.io/) - Gradient boosting library
- [LightGBM](https://lightgbm.readthedocs.io/) - Microsoft's gradient boosting
- [CatBoost](https://catboost.ai/docs/) - Yandex's boosting library
- [TensorFlow](https://www.tensorflow.org/) - Deep learning framework
- [SHAP](https://shap.readthedocs.io/) - Explainable AI library
- [Scikit-learn](https://scikit-learn.org/) - ML toolkit

### Security & Best Practices
- [ConsenSys Smart Contract Best Practices](https://consensys.github.io/smart-contract-best-practices/)
- [OpenZeppelin Security](https://docs.openzeppelin.com/contracts/4.x/)
- [Ethereum.org Security](https://ethereum.org/en/developers/docs/smart-contracts/security/)
- [CertiK Insights](https://www.certik.com/resources/blog) - Security research

### DeFi Protocols
- [Uniswap V2 Docs](https://docs.uniswap.org/protocol/V2/introduction)
- [Uniswap V3 Docs](https://docs.uniswap.org/protocol/introduction)
- [PancakeSwap Docs](https://docs.pancakeswap.finance/)
- [QuickSwap Docs](https://docs.quickswap.exchange/)

### Internal Documentation
- `docs/ARCHITECTURE.md` - System architecture ve design patterns
- `docs/GETTING_STARTED.md` - Hızlı başlangıç rehberi
- `docs/XAI_IMPLEMENTATION.md` - XAI system detayları
- `backend/data/models/MODEL_PERFORMANCE.md` - ML model performance metrics

## ⚠️ Güvenlik Uyarısı & Yasal Bildirim

### 🚨 Önemli Uyarılar

Bu araç **yatırım tavsiyesi DEĞİLDİR** ve sonuçları %100 doğru DEĞİLDİR. 

**Kısıtlamalar:**
- ❌ Gelecekteki rug pull'ları garanti edemez
- ❌ Smart contract bug'larını tespit edemeyebilir
- ❌ Developer intent'i okuyamaz
- ❌ Market manipulation'ı öngöremez
- ❌ Off-chain risk faktörlerini analiz edemez

**Her zaman yapmanız gerekenler:**
- ✅ **DYOR (Do Your Own Research)** - Kendi araştırmanızı yapın
- ✅ **Audit Raporları** - CertiK, PeckShield gibi firmaların raporlarını okuyun
- ✅ **Topluluk Araştırması** - Reddit, Twitter, Discord topluluklarını inceleyin
- ✅ **Kaybedeceğiniz Kadar Yatırım** - Sadece risk alabileceğiniz miktarı yatırın
- ✅ **Diversification** - Portföyünüzü çeşitlendirin
- ✅ **Exit Strategy** - Kar ve zarar limitlerinizi belirleyin

### 📜 Yasal Bildirim

**Sorumluluk Reddi:**
- Bu yazılım "OLDUĞU GİBİ" sunulmaktadır
- Hiçbir garanti verilmemektedir (açık veya zımni)
- Kullanımdan kaynaklanan zararlardan sorumluluk kabul edilmez
- Finansal kayıplardan yazılım geliştiricileri sorumlu tutulamaz

**Kullanım Şartları:**
- API rate limit'lere saygı gösterin
- Blockchain node'larını abuse etmeyin
- Illegal aktiviteler için kullanmayın

**Data Privacy:**
- Analiz geçmişi local'de saklanır
- Kişisel veri toplamıyoruz
- Blockchain verileri public'tir
- Üçüncü parti API'lar kendi privacy policy'lerine tabidir

### 🔒 Güvenlik Önerileri

**Token Yatırımı Yapan Kullanıcılar İçin:**
1. **Liquidity Lock** - Likiditenin ne kadar süre kilitli olduğunu kontrol edin
2. **Holder Distribution** - Top 10 holder %50'nin altında olmalı
3. **Contract Verification** - Kontrat mutlaka verified olmalı
4. **Honeypot Test** - Token'ı satabildiğinizden emin olun
5. **Tax Rates** - %10'dan yüksek tax şüphelidir
6. **Developer Transparency** - Doxxed team mi? LinkedIn profilleri var mı?
7. **Audit Reports** - En az 1 güvenilir audit firm raporu
8. **Community Sentiment** - Topluluk ne düşünüyor?

**DeFi Geliştirici İçin:**
- ⚠️ Bu tool'u production'da kendi sorumluluğunuzda kullanın
- ⚠️ API key'lerinizi `.env` dosyasında saklayın 
- ⚠️ Rate limiting ekleyin
- ⚠️ Input validation yapın
- ⚠️ Error handling ekleyin
- ⚠️ Logging ve monitoring setup yapın

## 📞 İletişim & Destek

### GitHub
- **Repository**: [github.com/TunahanKicci/defi-rugpull-detector](https://github.com/TunahanKicci/defi-rugpull-detector)




## 💡 Frequently Asked Questions (FAQ)

### Genel Sorular

**Q: Bu tool %100 doğru mu?**
A: Hayır. Hiçbir analiz tool'u %100 doğru olamaz. Bu bir risk değerlendirme aracıdır, kesin yatırım tavsiyesi değildir.

**Q: Hangi blockchain'leri destekliyorsunuz?**
A: Şu anda Ethereum, BSC (Binance Smart Chain) ve Polygon. Yakında Avalanche, Arbitrum, Optimism gelecek.

**Q: Analiz ne kadar sürer?**
A: Ortalama 20-30 saniye. Blockchain RPC hızına ve token'ın complexity'sine bağlı.

**Q: API kullanımı ücretli mi?**
A: Şu anda ücretsiz. Gelecekte premium features için ücretli plan gelebilir.

**Q: Kendi blockchain node'uma bağlanabilir miyim?**
A: Evet! `.env` dosyasında `ETHEREUM_RPC_URL`'i kendi node'unuza set edebilirsiniz.

### Teknik Sorular

**Q: Python version gereksinimleri?**
A: Python 3.10+ (3.10 ve 3.11 test edildi). Python 3.12 için bazı dependency'ler sorunlu olabilir.

**Q: Docker ile çalıştırabilir miyim?**
A: Evet! `docker-compose up` ile hem backend hem frontend başlatılabilir.

**Q: API rate limiting var mı?**
A: Evet, middleware'de rate limiter var. Default: 100 request/dakika/IP.

**Q: Cache sistemi nasıl çalışıyor?**
A: Redis kullanılıyor. Aynı token için 1 saat içinde tekrar analiz yapılmaz (force_refresh=true olmadıkça).

**Q: ML modellerini nasıl re-train edebilirim?**
A: `python train_models.py --generate --samples 1000` komutuyla sentetik data ile train edilebilir.

### Güvenlik Sorular

**Q: API key'lerimi nasıl saklarım?**
A: `.env` dosyasında saklayın ve `.gitignore`'a ekleyin. ASLA GitHub'a commit etmeyin!

**Q: Bu tool benim cüzdan bilgilerimi alıyor mu?**
A: Hayır! Sadece token contract address'i analiz ediyoruz. Cüzdan bağlantısı YOK.

**Q: Verilerim nereye gidiyor?**
A: Hiçbir yere! Tüm analiz local'de yapılıyor. Sadece blockchain RPC ve Etherscan API'ye request gidiyor.

---

## 📊 Proje Metrikleri

```
Lines of Code:      15,000+
Python Files:       45+
React Components:   20+
ML Models:          5
API Endpoints:      8
Test Coverage:      65%
Documentation:      90%
```
