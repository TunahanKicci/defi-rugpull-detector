# 🛡️ DeFi Rug Pull Detector

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)

Merkeziyetsiz finans (DeFi) alanındaki yatırımcıları dolandırıcılıklara (özellikle **rug pull**'lara) karşı korumayı amaçlayan, makine öğrenimi tabanlı risk analiz aracı.

![Demo Screenshot](docs/images/demo.png)

> ⚠️ **Disclaimer**: Bu araç sadece bilgilendirme amaçlıdır ve yatırım tavsiyesi değildir. Her zaman kendi araştırmanızı yapın (DYOR).

## 🎯 Özellikler

- ✅ Akıllı kontrat güvenlik taraması
- 📊 Token holder dağılım analizi
- 💧 Likidite havuzu durumu kontrolü
- 🔍 Transfer anomali tespiti
- 🎯 Scam pattern matching
- 💰 Tokenomik inceleme
- ⚡ Gerçek zamanlı monitoring
- 🤖 ML tabanlı risk skorlama (0-100)

## 🏗️ Teknoloji Stack

### Backend
- **FastAPI** - REST API framework
- **Web3.py** - Blockchain etkileşimi
- **Scikit-learn / XGBoost** - ML modelleri
- **Redis** - Önbellekleme
- **MongoDB** - Veri depolama

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Recharts** - Grafikler
- **Axios** - API client

## 📦 Kurulum

### Gereksinimler
- Python 3.10+
- Node.js 18+
- Redis (opsiyonel)
- MongoDB (opsiyonel)

### Backend Kurulum

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# .env dosyasını düzenleyin
python main.py
```

### Frontend Kurulum

```bash
cd frontend
npm install
cp .env.example .env
# .env dosyasını düzenleyin
npm run dev
```

## 🚀 Kullanım

1. Uygulamayı başlatın
2. Token kontrat adresini girin (Ethereum, BSC, Polygon)
3. Analiz sonuçlarını bekleyin
4. Risk skorunu ve detayları inceleyin

## 📡 API Endpoints

- `POST /api/analyze/{address}` - Token analizi
- `GET /api/monitor/{address}` - Gerçek zamanlı izleme
- `GET /api/history` - Geçmiş analizler
- `GET /health` - Health check

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen `CONTRIBUTING.md` dosyasını inceleyin.

## 📄 Lisans

MIT License - Detaylar için `LICENSE` dosyasına bakın.

## 📊 Demo & Screenshots

(Buraya ekran görüntüleri eklenebilir)

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work*

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Web3.py for blockchain interactions
- React community for amazing tools
- All open-source contributors

## ⚠️ Uyarı

Bu araç yatırım tavsiyesi değildir. Kendi araştırmanızı yapın ve risk alırken dikkatli olun.

---

**Made with ❤️ for the DeFi community**
