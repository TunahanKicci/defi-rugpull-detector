# 🏗️ System Architecture

## Overview

RugPull Detector is a full-stack application consisting of:

- **Backend**: FastAPI-based REST API with ML models
- **Frontend**: React SPA with real-time updates
- **Analysis Modules**: 6 specialized analysis modules
- **ML Pipeline**: Risk scoring and anomaly detection

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Home   │  │ Analysis │  │ Monitor  │  │ History  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/WebSocket
┌───────────────────────┴─────────────────────────────────────┐
│                     Backend (FastAPI)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              API Layer (Routers)                        │ │
│  │  /analyze  /monitor  /history  /health                 │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                       │
│  ┌────────────────────┴───────────────────────────────────┐ │
│  │          Analysis Orchestrator                          │ │
│  │  (Coordinates all modules and ML scoring)              │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                       │
│  ┌────────────────────┴───────────────────────────────────┐ │
│  │              Analysis Modules                           │ │
│  │  A) Contract Security  D) Transfer Anomaly             │ │
│  │  B) Holder Analysis    E) Pattern Matching             │ │
│  │  C) Liquidity Pool     F) Tokenomics                   │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                       │
│  ┌────────────────────┴───────────────────────────────────┐ │
│  │          ML Risk Scorer (XGBoost)                       │ │
│  │  Feature extraction → Model prediction → Explainability│ │
│  └────────────────────┬───────────────────────────────────┘ │
└───────────────────────┴─────────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────────┐
│              External Data Sources                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Blockchain  │  │   Etherscan  │  │  Scam DB     │      │
│  │  RPC Nodes   │  │   APIs       │  │  (Local)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### Frontend (React + Vite)

**Technology Stack:**
- React 18 with Hooks
- React Router for navigation
- Axios for API communication
- Tailwind CSS for styling
- Recharts for data visualization

**Key Components:**
- `Home.jsx`: Search interface
- `AnalysisResult.jsx`: Display comprehensive results
- `Monitor.jsx`: Real-time WebSocket monitoring
- `History.jsx`: Past analyses

### Backend (FastAPI)

**Technology Stack:**
- FastAPI for REST API
- Web3.py for blockchain interaction
- Scikit-learn/XGBoost for ML
- Pydantic for data validation
- Uvicorn as ASGI server

**Key Services:**
- `analysis_orchestrator.py`: Coordinates analysis workflow
- `cache_manager.py`: Result caching
- `websocket_manager.py`: Real-time event streaming

### Analysis Modules

Each module is independent and returns:
- `risk_score`: 0-100 risk score
- `warnings`: List of issues found
- `data`: Module-specific data
- `features`: Numerical features for ML

**Module A: Contract Security**
- Bytecode analysis
- Dangerous function detection
- Proxy/upgradeable check

**Module B: Holder Analysis**
- Top holder concentration
- Gini coefficient
- Whale detection

**Module C: Liquidity Pool**
- LP lock verification
- Liquidity amount check
- LP/MarketCap ratio

**Module D: Transfer Anomaly**
- Large transfer detection
- Mint event tracking
- Pattern anomalies

**Module E: Pattern Matching**
- Known scam database lookup
- Bytecode similarity
- Honeypot patterns

**Module F: Tokenomics**
- Buy/sell tax analysis
- Transaction limits
- Fee structure review

### ML Pipeline

**Risk Scoring Model:**
- Input: Features from all modules
- Processing: XGBoost classifier
- Output: Risk score (0-100) + explanations

**Feature Engineering:**
- Numerical features extracted from each module
- Normalized to 0-1 range
- ~50 total features

**Explainability:**
- SHAP values for feature importance
- Clear reasoning for risk scores

## Data Flow

1. **User Input**: Contract address + chain
2. **Validation**: Address format check
3. **Cache Check**: Look for cached results
4. **Data Collection**: Fetch blockchain data
5. **Module Execution**: Run all 6 modules in parallel
6. **Feature Extraction**: Convert module outputs to features
7. **ML Prediction**: Calculate final risk score
8. **Result Aggregation**: Combine all results
9. **Response**: Return to frontend

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│         Render.com (Production)          │
│                                          │
│  ┌────────────┐      ┌────────────┐    │
│  │  Frontend  │      │  Backend   │    │
│  │   (Node)   │◄────►│  (Python)  │    │
│  └────────────┘      └────────────┘    │
│                            │             │
│  ┌────────────┐      ┌────────────┐    │
│  │   Redis    │      │  MongoDB   │    │
│  │  (Cache)   │      │  (History) │    │
│  └────────────┘      └────────────┘    │
└─────────────────────────────────────────┘
```

## Security Considerations

- Rate limiting on API endpoints
- Input validation with Pydantic
- CORS configuration
- No sensitive data in responses
- API keys stored in environment variables

## Scalability

- Stateless backend (horizontal scaling)
- Redis for distributed caching
- Async/await for concurrent operations
- Database for historical data
- CDN for frontend assets

## Monitoring & Observability

- Health check endpoints
- Structured logging
- Error tracking
- Performance metrics
- API usage analytics
