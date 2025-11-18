# 🚀 Başlangıç Rehberi

## Ön Gereksinimler

- **Python 3.10+**
- **Node.js 18+**
- **Git**

## 📦 Kurulum Adımları

### 1. Repository'yi Klonlayın

```bash
git clone <repository-url>
cd proje2
```

### 2. Backend Kurulumu

```bash
# Sanal ortam oluşturun (önerilen)
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# .env dosyasını oluşturun
copy .env.example .env

# .env dosyasını düzenleyin ve API anahtarlarınızı ekleyin
```

### 3. Frontend Kurulumu

```bash
cd frontend
npm install
copy .env.example .env
cd ..
```

### 4. Uygulamayı Çalıştırın

#### Backend'i Başlatın

```bash
# Backend dizininden
python backend/main.py
```

Backend şu adreste çalışacak: `http://localhost:8000`

API Dokümantasyonu: `http://localhost:8000/docs`

#### Frontend'i Başlatın

Yeni bir terminal penceresi açın:

```bash
cd frontend
npm run dev
```

Frontend şu adreste çalışacak: `http://localhost:5173`

## 🔑 API Anahtarları

Ücretsiz API anahtarları edinmek için:

- **Etherscan**: https://etherscan.io/apis
- **BSCScan**: https://bscscan.com/apis  
- **PolygonScan**: https://polygonscan.com/apis

`.env` dosyanızda bu anahtarları güncelleyin:

```env
ETHERSCAN_API_KEY=your-key-here
BSCSCAN_API_KEY=your-key-here
POLYGONSCAN_API_KEY=your-key-here
```

## 🐳 Docker ile Çalıştırma (Opsiyonel)

```bash
docker-compose up
```

Bu komut hem backend hem de frontend'i başlatır.

## 🧪 Test Etme

Örnek bir token analizi:

1. Frontend'e gidin: http://localhost:5173
2. Bir token kontrat adresi girin (örn: `0x...`)
3. Blockchain seçin (Ethereum, BSC, Polygon)
4. "Analyze Contract" butonuna tıklayın

## 📝 Not

- İlk çalıştırmada bazı modüller mock data kullanabilir
- Production için gerçek API entegrasyonları eklemelisiniz
- ML modelleri eğitilmesi gerekiyor (h_ml_risk_scorer.py)

## 🆘 Sorun Giderme

**Backend başlamıyor:**
- Python versiyonunu kontrol edin: `python --version`
- Bağımlılıkları tekrar yükleyin: `pip install -r requirements.txt`

**Frontend başlamıyor:**
- Node versiyonunu kontrol edin: `node --version`
- node_modules'ü silin ve tekrar yükleyin: `rm -rf node_modules && npm install`

**RPC bağlantı hatası:**
- `.env` dosyanızdaki RPC URL'lerini kontrol edin
- Alternatif ücretsiz RPC'ler deneyin

## 📚 Daha Fazla Bilgi

- API Dokümantasyonu: `/docs` klasörü
- Module açıklamaları: Her modülün başında docstring
- Mimari diyagram: `proje_mimari.txt`
