# Docker Kurulumu Tamamlandı ✅

## 📋 Oluşturulan Dosyalar

### Docker Compose Dosyaları
- ✅ `docker-compose.yml` - Base configuration
- ✅ `docker-compose.override.yml` - Development overrides
- ✅ `docker-compose.prod.yml` - Production configuration
- ✅ `.dockerignore` - Docker ignore rules

### Docker Başlatma Betikleri

#### Windows Batch Dosyaları
- ✅ `docker-start-dev.bat` - Development ortamını başlat
- ✅ `docker-start-prod.bat` - Production ortamını başlat
- ✅ `docker-stop.bat` - Servisleri durdur
- ✅ `docker-logs.bat` - Logları izle

#### Linux/macOS Shell Dosyaları
- ✅ `docker-start-dev.sh` - Development ortamını başlat
- ✅ `docker-start-prod.sh` - Production ortamını başlat
- ✅ `docker-stop.sh` - Servisleri durdur
- ✅ `docker-logs.sh` - Logları izle

### Frontend Dosyaları
- ✅ `frontend/nginx.conf` - Production Nginx configuration
- ✅ `frontend/Dockerfile` - Updated for Nginx production

### Dokumentasyon
- ✅ `docs/DOCKER.md` - Detaylı Docker rehberi
- ✅ `README.md` - Docker bölümü eklendi

## 🚀 Hızlı Başlangıç

### Windows
```powershell
# Development ortamını başlat
.\docker-start-dev.bat

# Veya dosyayı double-click yapın
```

### Linux/macOS
```bash
# Permission'ları ayarla
chmod +x docker-*.sh

# Development ortamını başlat
./docker-start-dev.sh
```

## 📍 Erişim Noktaları

### Development
```
Frontend:      http://localhost:5173
Backend API:   http://localhost:8000
API Docs:      http://localhost:8000/docs
Redis:         localhost:6379
MongoDB:       localhost:27017
```

### Production
```
Frontend:      http://localhost
Backend API:   http://localhost:8000
API Docs:      http://localhost:8000/docs
```

## 🐳 Servisler

### Backend
- Image: `python:3.10-slim`
- Framework: FastAPI + Uvicorn
- Port: 8000
- Hot reload: Etkinleştirildi (development)

### Frontend
- Image: `nginx:alpine` (production) / `node:18-alpine` (dev)
- Port: 80 (production) / 5173 (development)
- Gzip compression: Etkinleştirildi
- API proxy: Yapılandırıldı

### Redis
- Image: `redis:7-alpine`
- Port: 6379
- Persistence: AOF enabled

### MongoDB
- Image: `mongo:7`
- Port: 27017
- Database: `rugpulldetector`

## 📚 Yararlı Komutlar

### Logları İzle
```bash
# Tüm servislerin logları
docker-compose logs -f

# Spesifik servis
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Servisleri Yönet
```bash
# Servisleri başlat
docker-compose up -d

# Servisleri durdur
docker-compose down

# Servisleri yeniden başlat
docker-compose restart

# Servis durumunu kontrol et
docker-compose ps
```

### Shell Erişimi
```bash
# Backend'e erişim
docker-compose exec backend bash

# Frontend'e erişim
docker-compose exec frontend sh

# MongoDB'ye erişim
docker-compose exec mongodb mongosh

# Redis'e erişim
docker-compose exec redis redis-cli
```

## ⚙️ Konfigürasyon

### .env Dosyası
- `APP_ENV=development` - Development modunda çalışır
- `DEBUG=true` - Debug loggingı etkinleştirildi
- API Keys ve RPC endpoints yapılandırıldı

### Environment Variables
Docker Compose otomatik olarak `.env` dosyasını yükler:
```bash
# .env dosyasından oku
env_file:
  - .env
```

## 🔧 Production Deployment

```bash
# Production dosyalarını kullan
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Veya batch dosyasını kullan
docker-start-prod.bat
```

**Production öncesi kontrol listesi:**
- [ ] `.env` dosyasında SECRET_KEY değiştirildi
- [ ] DEBUG=false ayarlandı
- [ ] API Keys güncellendi
- [ ] CORS_ORIGINS ayarlandı
- [ ] Database şifrelemeleri yapıldı
- [ ] Reverse proxy (SSL/TLS) kuruldu

## 📚 Detaylı Rehber

Daha detaylı bilgi için: [docs/DOCKER.md](../docs/DOCKER.md)

## ❓ Sorun Giderme

### Docker başlamıyorsa
```bash
# Docker Desktop'ı açın ve çalıştırdığını kontrol edin
docker --version
docker-compose --version
```

### Port zaten kullanılıyorsa
`docker-compose.yml`'de port numaralarını değiştirin:
```yaml
ports:
  - "9000:8000"  # Backend
  - "5174:5173"  # Frontend
```

### Image oluşturulamıyorsa
```bash
# Cache'i temizle
docker-compose build --no-cache
```

### Bağlantı problemi
```bash
# Network durumunu kontrol et
docker-compose ps

# Container loglarını kontrol et
docker-compose logs [service-name]
```

## 🎯 Sonraki Adımlar

1. ✅ Docker kurulumu tamamlandı
2. 🔄 `docker-start-dev.bat` ile ortamı başlat
3. 🌐 http://localhost:5173 adresini ziyaret et
4. 🧪 Test analizi çalıştır
5. 📖 Detaylı rehber için `docs/DOCKER.md` okuyun

## 📞 Destek

- Frontend hatası: `docker-compose logs -f frontend`
- Backend hatası: `docker-compose logs -f backend`
- Database hatası: `docker-compose logs -f mongodb`
- Cache hatası: `docker-compose logs -f redis`

---

**Docker kurulumu başarıyla tamamlandı!** 🎉
