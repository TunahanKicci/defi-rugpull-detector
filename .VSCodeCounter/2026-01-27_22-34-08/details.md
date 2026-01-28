# Details

Date : 2026-01-27 22:34:08

Directory c:\\proje2

Total : 102 files,  18570 codes, 1842 comments, 2086 blanks, all 22498 lines

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [.dockerignore](/.dockerignore) | Ignore | 26 | 5 | 5 | 36 |
| [README.md](/README.md) | Markdown | 742 | 0 | 174 | 916 |
| [backend/Dockerfile](/backend/Dockerfile) | Docker | 12 | 4 | 8 | 24 |
| [backend/\_\_init\_\_.py](/backend/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [backend/api/\_\_init\_\_.py](/backend/api/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [backend/api/middleware/\_\_init\_\_.py](/backend/api/middleware/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [backend/api/middleware/cors.py](/backend/api/middleware/cors.py) | Python | 12 | 9 | 3 | 24 |
| [backend/api/middleware/error\_handler.py](/backend/api/middleware/error_handler.py) | Python | 27 | 9 | 8 | 44 |
| [backend/api/middleware/rate\_limiter.py](/backend/api/middleware/rate_limiter.py) | Python | 49 | 27 | 21 | 97 |
| [backend/api/models/\_\_init\_\_.py](/backend/api/models/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [backend/api/models/request.py](/backend/api/models/request.py) | Python | 28 | 7 | 9 | 44 |
| [backend/api/models/response.py](/backend/api/models/response.py) | Python | 72 | 16 | 21 | 109 |
| [backend/api/routers/\_\_init\_\_.py](/backend/api/routers/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [backend/api/routers/analysis.py](/backend/api/routers/analysis.py) | Python | 65 | 27 | 16 | 108 |
| [backend/api/routers/health.py](/backend/api/routers/health.py) | Python | 17 | 14 | 6 | 37 |
| [backend/api/routers/history.py](/backend/api/routers/history.py) | Python | 50 | 26 | 14 | 90 |
| [backend/api/routers/monitoring.py](/backend/api/routers/monitoring.py) | Python | 87 | 24 | 24 | 135 |
| [backend/catboost\_info/catboost\_training.json](/backend/catboost_info/catboost_training.json) | JSON | 104 | 0 | 0 | 104 |
| [backend/catboost\_info/learn\_error.tsv](/backend/catboost_info/learn_error.tsv) | TSV | 101 | 0 | 1 | 102 |
| [backend/catboost\_info/time\_left.tsv](/backend/catboost_info/time_left.tsv) | TSV | 101 | 0 | 1 | 102 |
| [backend/check\_models.py](/backend/check_models.py) | Python | 49 | 4 | 7 | 60 |
| [backend/config/\_\_init\_\_.py](/backend/config/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [backend/config/chains.py](/backend/config/chains.py) | Python | 50 | 5 | 7 | 62 |
| [backend/config/settings.py](/backend/config/settings.py) | Python | 55 | 21 | 21 | 97 |
| [backend/data/models/MODEL\_PERFORMANCE.md](/backend/data/models/MODEL_PERFORMANCE.md) | Markdown | 120 | 0 | 41 | 161 |
| [backend/data/scam\_database/known\_scams.json](/backend/data/scam_database/known_scams.json) | JSON | 17 | 0 | 1 | 18 |
| [backend/data/training\_data.csv](/backend/data/training_data.csv) | CSV | 1,001 | 0 | 1 | 1,002 |
| [backend/main.py](/backend/main.py) | Python | 60 | 16 | 20 | 96 |
| [backend/modules/\_\_init\_\_.py](/backend/modules/__init__.py) | Python | 22 | 3 | 1 | 26 |
| [backend/modules/a\_contract\_security.py](/backend/modules/a_contract_security.py) | Python | 266 | 104 | 77 | 447 |
| [backend/modules/b\_holder\_analysis.py](/backend/modules/b_holder_analysis.py) | Python | 360 | 85 | 81 | 526 |
| [backend/modules/c\_liquidity\_pool.py](/backend/modules/c_liquidity_pool.py) | Python | 337 | 85 | 66 | 488 |
| [backend/modules/d\_transfer\_anomaly.py](/backend/modules/d_transfer_anomaly.py) | Python | 459 | 70 | 77 | 606 |
| [backend/modules/e\_pattern\_matching.py](/backend/modules/e_pattern_matching.py) | Python | 248 | 101 | 81 | 430 |
| [backend/modules/f\_tokenomics.py](/backend/modules/f_tokenomics.py) | Python | 362 | 99 | 65 | 526 |
| [backend/modules/h\_ml\_risk\_scorer.py](/backend/modules/h_ml_risk_scorer.py) | Python | 169 | 49 | 47 | 265 |
| [backend/modules/i\_honeypot\_simulator.py](/backend/modules/i_honeypot_simulator.py) | Python | 457 | 71 | 86 | 614 |
| [backend/modules/k\_whale\_detector.py](/backend/modules/k_whale_detector.py) | Python | 261 | 69 | 74 | 404 |
| [backend/modules/ml/\_\_init\_\_.py](/backend/modules/ml/__init__.py) | Python | 0 | 4 | 1 | 5 |
| [backend/modules/ml/deep\_model.py](/backend/modules/ml/deep_model.py) | Python | 152 | 69 | 46 | 267 |
| [backend/modules/ml/ensemble\_model.py](/backend/modules/ml/ensemble_model.py) | Python | 249 | 56 | 50 | 355 |
| [backend/modules/ml/feature\_extractor.py](/backend/modules/ml/feature_extractor.py) | Python | 84 | 24 | 18 | 126 |
| [backend/modules/ml/train\_whale\_model.py](/backend/modules/ml/train_whale_model.py) | Python | 123 | 47 | 32 | 202 |
| [backend/modules/xai\_explainer.py](/backend/modules/xai_explainer.py) | Python | 395 | 76 | 79 | 550 |
| [backend/requirements.txt](/backend/requirements.txt) | pip requirements | 36 | 14 | 14 | 64 |
| [backend/run.bat](/backend/run.bat) | Batch | 3 | 0 | 1 | 4 |
| [backend/services/\_\_init\_\_.py](/backend/services/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [backend/services/analysis\_orchestrator.py](/backend/services/analysis_orchestrator.py) | Python | 253 | 62 | 51 | 366 |
| [backend/services/blockchain/\_\_init\_\_.py](/backend/services/blockchain/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [backend/services/blockchain/base\_chain.py](/backend/services/blockchain/base_chain.py) | Python | 92 | 69 | 21 | 182 |
| [backend/services/blockchain/bsc.py](/backend/services/blockchain/bsc.py) | Python | 55 | 16 | 17 | 88 |
| [backend/services/blockchain/ethereum.py](/backend/services/blockchain/ethereum.py) | Python | 55 | 18 | 17 | 90 |
| [backend/services/blockchain/polygon.py](/backend/services/blockchain/polygon.py) | Python | 55 | 16 | 17 | 88 |
| [backend/services/cache\_manager.py](/backend/services/cache_manager.py) | Python | 43 | 47 | 18 | 108 |
| [backend/services/websocket\_manager.py](/backend/services/websocket_manager.py) | Python | 89 | 73 | 31 | 193 |
| [backend/start\_backend.bat](/backend/start_backend.bat) | Batch | 6 | 0 | 2 | 8 |
| [backend/start\_backend.sh](/backend/start_backend.sh) | Shell Script | 3 | 1 | 2 | 6 |
| [backend/test\_ml.py](/backend/test_ml.py) | Python | 86 | 7 | 15 | 108 |
| [backend/train\_models.py](/backend/train_models.py) | Python | 201 | 51 | 65 | 317 |
| [backend/utils/\_\_init\_\_.py](/backend/utils/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [backend/utils/constants.py](/backend/utils/constants.py) | Python | 56 | 16 | 15 | 87 |
| [backend/utils/formatters.py](/backend/utils/formatters.py) | Python | 48 | 28 | 19 | 95 |
| [backend/utils/logger.py](/backend/utils/logger.py) | Python | 33 | 16 | 11 | 60 |
| [backend/utils/validators.py](/backend/utils/validators.py) | Python | 24 | 51 | 14 | 89 |
| [docker-compose.prod.yml](/docker-compose.prod.yml) | YAML | 28 | 0 | 4 | 32 |
| [docker-compose.yml](/docker-compose.yml) | YAML | 27 | 0 | 4 | 31 |
| [docker-start.bat](/docker-start.bat) | Batch | 43 | 2 | 7 | 52 |
| [docs/ARCHITECTURE.md](/docs/ARCHITECTURE.md) | Markdown | 159 | 0 | 35 | 194 |
| [docs/DOCKER.md](/docs/DOCKER.md) | Markdown | 197 | 0 | 66 | 263 |
| [docs/GETTING\_STARTED.md](/docs/GETTING_STARTED.md) | Markdown | 87 | 0 | 43 | 130 |
| [frontend/Dockerfile](/frontend/Dockerfile) | Docker | 7 | 0 | 6 | 13 |
| [frontend/index.html](/frontend/index.html) | HTML | 14 | 0 | 1 | 15 |
| [frontend/nginx.conf](/frontend/nginx.conf) | Properties | 45 | 6 | 8 | 59 |
| [frontend/package-lock.json](/frontend/package-lock.json) | JSON | 7,867 | 0 | 1 | 7,868 |
| [frontend/package.json](/frontend/package.json) | JSON | 35 | 0 | 1 | 36 |
| [frontend/postcss.config.js](/frontend/postcss.config.js) | JavaScript | 6 | 0 | 1 | 7 |
| [frontend/src/App.jsx](/frontend/src/App.jsx) | JavaScript JSX | 28 | 0 | 3 | 31 |
| [frontend/src/components/Layout/Footer.jsx](/frontend/src/components/Layout/Footer.jsx) | JavaScript JSX | 66 | 4 | 7 | 77 |
| [frontend/src/components/Layout/Header.jsx](/frontend/src/components/Layout/Header.jsx) | JavaScript JSX | 73 | 5 | 9 | 87 |
| [frontend/src/data/ethereumTokens.js](/frontend/src/data/ethereumTokens.js) | JavaScript | 87 | 1 | 3 | 91 |
| [frontend/src/main.jsx](/frontend/src/main.jsx) | JavaScript JSX | 7 | 0 | 2 | 9 |
| [frontend/src/pages/About.jsx](/frontend/src/pages/About.jsx) | JavaScript JSX | 76 | 1 | 4 | 81 |
| [frontend/src/pages/AnalysisResult.jsx](/frontend/src/pages/AnalysisResult.jsx) | JavaScript JSX | 967 | 60 | 74 | 1,101 |
| [frontend/src/pages/History.jsx](/frontend/src/pages/History.jsx) | JavaScript JSX | 12 | 0 | 1 | 13 |
| [frontend/src/pages/Home.jsx](/frontend/src/pages/Home.jsx) | JavaScript JSX | 135 | 12 | 19 | 166 |
| [frontend/src/pages/Monitor.jsx](/frontend/src/pages/Monitor.jsx) | JavaScript JSX | 12 | 0 | 1 | 13 |
| [frontend/src/pages/NotFound.jsx](/frontend/src/pages/NotFound.jsx) | JavaScript JSX | 14 | 0 | 2 | 16 |
| [frontend/src/services/analysisService.js](/frontend/src/services/analysisService.js) | JavaScript | 13 | 13 | 3 | 29 |
| [frontend/src/services/api.js](/frontend/src/services/api.js) | JavaScript | 22 | 1 | 5 | 28 |
| [frontend/src/styles/index.css](/frontend/src/styles/index.css) | PostCSS | 109 | 2 | 23 | 134 |
| [frontend/start\_frontend.bat](/frontend/start_frontend.bat) | Batch | 5 | 0 | 2 | 7 |
| [frontend/start\_frontend.sh](/frontend/start_frontend.sh) | Shell Script | 3 | 1 | 2 | 6 |
| [frontend/tailwind.config.js](/frontend/tailwind.config.js) | JavaScript | 45 | 1 | 1 | 47 |
| [frontend/vite.config.js](/frontend/vite.config.js) | JavaScript | 17 | 1 | 2 | 20 |
| [k8s/deployment.yaml](/k8s/deployment.yaml) | YAML | 26 | 0 | 0 | 26 |
| [k8s/service.yaml](/k8s/service.yaml) | YAML | 12 | 0 | 0 | 12 |
| [render.yaml](/render.yaml) | YAML | 46 | 7 | 2 | 55 |
| [requirements.txt](/requirements.txt) | pip requirements | 35 | 14 | 14 | 63 |
| [tests/performance\_reports/SUMMARY.md](/tests/performance_reports/SUMMARY.md) | Markdown | 73 | 0 | 31 | 104 |
| [tests/performance\_reports/deep\_analysis\_benchmark.md](/tests/performance_reports/deep_analysis_benchmark.md) | Markdown | 99 | 0 | 27 | 126 |
| [tests/performance\_reports/infrastructure\_benchmark.md](/tests/performance_reports/infrastructure_benchmark.md) | Markdown | 114 | 0 | 32 | 146 |
| [tests/quality/REPORT.md](/tests/quality/REPORT.md) | Markdown | 32 | 0 | 11 | 43 |

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)