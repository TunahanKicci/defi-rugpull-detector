# 🛡️ DeFi Rug Pull Detector

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)
[![ML Models](https://img.shields.io/badge/ML-XGBoost%20%7C%20LightGBM%20%7C%20CatBoost%20%7C%20TensorFlow-orange.svg)](https://github.com/)

Merkeziyetsiz finans (DeFi) alanındaki yatırımcıları dolandırıcılıklara (özellikle **rug pull**'lara) karşı korumayı amaçlayan, **ensemble ML modelleri** ile desteklenen gerçek zamanlı risk analiz platformu.

> ⚠️ **Disclaimer**: Bu araç sadece bilgilendirme amaçlıdır ve yatırım tavsiyesi değildir. Her zaman kendi araştırmanızı yapın (DYOR).

## 🎯 Özellikler

### 🔍 Analiz Modülleri
- ✅ **Contract Security** - Akıllı kontrat güvenlik taraması (SELFDESTRUCT, DelegateCall, Proxy kontrolleri)
- 📊 **Holder Analysis** - Token holder dağılım analizi (Gini katsayısı, concentration metrics)
- 💧 **Liquidity Pool** - Likidite havuzu durumu ve lock kontrolü (Uniswap V2/V3, PancakeSwap)
- 🔍 **Transfer Anomaly** - Anormal transfer patternleri ve mint/burn tespiti
- 🎯 **Pattern Matching** - Bilinen scam pattern'leri ve honeypot kontrolleri
- 💰 **Tokenomics** - Token ekonomisi ve tax yapısı analizi

### 🤖 ML Ensemble Sistemi
- **XGBoost** - Gradient boosting classifier (85.8% accuracy)
- **LightGBM** - Hafif ve hızlı gradient boosting (79.7% accuracy)
- **CatBoost** - Categorical boosting (66.1% accuracy)
- **Deep Neural Network** - TensorFlow/Keras ile 4-layer DNN (75.2% accuracy)
- **Ensemble Prediction** - 4 modelin weighted voting ile kombinasyonu
- **Feature Engineering** - 40 özellik otomatik çıkarımı

### ⚡ Ek Özellikler
- 🔄 **Auto-reload** - Kod değişikliklerinde otomatik yeniden başlatma
- 📝 **Comprehensive Logging** - Detaylı analiz log kayıtları
- 🚀 **Async Architecture** - Non-blocking I/O ile yüksek performans
- 🎨 **Modern UI** - Responsive ve kullanıcı dostu arayüz
- 🌐 **Multi-chain Support** - Ethereum, BSC, Polygon desteği

## 🏗️ Teknoloji Stack

### Backend
- **FastAPI** - Modern async REST API framework
- **Web3.py** - Ethereum blockchain etkileşimi
- **Etherscan API V2** - On-chain data ve verified contract bilgileri
- **Chainlink Price Feeds** - Gerçek zamanlı fiyat dataları

### Machine Learning
- **TensorFlow 2.15** & **Keras 2.15** - Deep learning framework
- **XGBoost 2.0.3** - Gradient boosting classifier
- **LightGBM 4.2.0** - Microsoft'un hafif GB implementasyonu
- **CatBoost 1.2.2** - Yandex'in categorical boosting library
- **Scikit-learn 1.4.0** - Feature engineering ve metrics
- **NumPy & Pandas** - Data manipulation

### Frontend
- **React 18** - Component-based UI framework
- **Vite** - Lightning-fast build tool
- **Tailwind CSS 3** - Utility-first CSS framework
- **Recharts** - Data visualization
- **Axios** - HTTP client (120s timeout)

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

## 🚀 Kullanım

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
  "final_risk_score": 43.38,
  "risk_level": "MEDIUM",
  "ml_prediction": 78.3,
  "module_results": {
    "contract_security": {"risk_score": 30, "confidence": 100},
    "holder_analysis": {"risk_score": 15, "confidence": 90},
    "liquidity_pool": {"risk_score": 20, "confidence": 95},
    "transfer_anomaly": {"risk_score": 65, "confidence": 80},
    "pattern_matching": {"risk_score": 45, "confidence": 85},
    "tokenomics": {"risk_score": 0, "confidence": 80}
  },
  "ml_models": {
    "xgboost": 85.76,
    "lightgbm": 79.66,
    "catboost": 66.08,
    "deep_neural_network": 75.24,
    "ensemble": 78.30
  }
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
│   │   ├── middleware/           # CORS, rate limiting, error handling
│   │   └── models/               # Request/response models
│   ├── modules/                  # Analysis modules
│   │   ├── a_contract_security.py
│   │   ├── b_holder_analysis.py
│   │   ├── c_liquidity_pool.py
│   │   ├── d_transfer_anomaly.py
│   │   ├── e_pattern_matching.py
│   │   ├── f_tokenomics.py
│   │   ├── h_ml_risk_scorer.py
│   │   └── ml/                   # Machine learning
│   │       ├── ensemble_model.py
│   │       ├── feature_extractor.py
│   │       ├── deep_model.py
│   │       └── __init__.py
│   ├── services/                 # Business logic
│   │   ├── analysis_orchestrator.py
│   │   ├── cache_manager.py
│   │   └── blockchain/           # Chain integrations
│   ├── data/
│   │   └── models/               # Pre-trained ML models
│   │       ├── xgboost_model.pkl
│   │       ├── lightgbm_model.pkl
│   │       ├── catboost_model.pkl
│   │       └── deep_model.h5
│   ├── config/                   # Configuration
│   ├── utils/                    # Utilities
│   ├── train_models.py           # Model training script
│   ├── main.py                   # Application entry
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── pages/                # Page components
│   │   ├── services/             # API clients
│   │   └── styles/               # CSS files
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── docs/                         # Documentation
└── README.md
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm run test
```

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

**Contract Security (8)**
- has_bytecode, is_verified, has_selfdestruct
- has_delegatecall, is_proxy, has_owner
- is_pausable, contract_risk_score

**Holder Analysis (5)**
- top_10_concentration, top_holder_pct
- gini_coefficient, unique_holders
- holder_risk_score

**Liquidity Pool (4)**
- lp_locked, liquidity_usd
- has_pair, liquidity_risk_score

**Transfer Anomaly (7)**
- mint_count, burn_count
- unique_senders, unique_receivers
- avg_transfer_value, anomaly_score
- transfer_risk_score

**Pattern Matching (4)**
- is_known_scam, honeypot_pattern
- similarity_score, pattern_risk_score

**Tokenomics (6)**
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
| XGBoost | 87.0% | 86.6% | 92.4% | 89.4% | 86.4% |
| LightGBM | 87.0% | 86.6% | 92.4% | 89.4% | 86.4% |
| CatBoost | 87.0% | 86.6% | 92.4% | 89.4% | 86.4% |
| Deep NN | 84.0% | 84.0% | 100% | 91.3% | 66.3% |
| **Ensemble** | **87.0%** | **86.6%** | **92.4%** | **89.4%** | **86.4%** |

*Trained on 1000 synthetic samples (840 rug pulls, 160 safe tokens)*

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Şu adımları takip edebilirsiniz:

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

### Development Guidelines

- Code style: PEP 8 (Python), ESLint (JavaScript)
- Commit messages: Conventional Commits
- Tests: Her yeni feature için test yazın
- Documentation: Code'u dokümante edin

## 🐛 Bilinen Sorunlar

- Windows'ta emoji karakterleri terminal encoding sorununa neden olabilir
- Bazı proxy kontratlar için bytecode analizi sınırlıdır
- Yüksek transaction volume'lu tokenlarda API rate limiting olabilir

## 🔮 Roadmap

- [ ] Web3 wallet entegrasyonu (MetaMask)
- [ ] Real-time WebSocket monitoring
- [ ] Historical price correlation analysis
- [ ] Social media sentiment analysis
- [ ] Multi-language support (EN, TR, ZH)
- [ ] Mobile app (React Native)
- [ ] Advanced ML models (Transformer-based)
- [ ] DAO governance token analysis

## 📄 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👥 Yazarlar

- **Tunahan Kıcı** - *Initial work* - [TunahanKicci](https://github.com/TunahanKicci)

## 🙏 Teşekkürler

- **Etherscan** - Comprehensive blockchain data API
- **Chainlink** - Decentralized price feeds
- **FastAPI** - Modern Python web framework
- **TensorFlow** - Machine learning framework
- **Web3.py** - Ethereum library
- **React** & **Vite** - Frontend excellence
- **Open source community** - Amazing tools and libraries

## 📚 Kaynaklar

- [Etherscan API Documentation](https://docs.etherscan.io/)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [DeFi Security Best Practices](https://github.com/ConsenSys/smart-contract-best-practices)

## ⚠️ Güvenlik Uyarısı

Bu araç **yatırım tavsiyesi değildir**. Sonuçlar %100 doğru değildir ve sadece referans amaçlıdır. 

**Her zaman:**
- ✅ Kendi araştırmanızı yapın (DYOR)
- ✅ Audit raporlarını kontrol edin
- ✅ Topluluk görüşlerini değerlendirin
- ✅ Kaybedeceğiniz kadar risk alın
- ❌ Körü körüne güvenmeyin

## 📞 İletişim

- **GitHub**: [@TunahanKicci](https://github.com/TunahanKicci)
- **Issues**: [GitHub Issues](https://github.com/TunahanKicci/defi-rugpull-detector/issues)
- **Discussions**: [GitHub Discussions](https://github.com/TunahanKicci/defi-rugpull-detector/discussions)

---

**Made with ❤️ for the DeFi community** 

*Protecting investors, one analysis at a time* 🛡️
