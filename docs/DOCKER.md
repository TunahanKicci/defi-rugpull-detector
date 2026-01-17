# Docker Setup Guide

Bu rehber, DeFi Rug Pull Detector projesini Docker ile nasıl çalıştıracağınızı açıklamaktadır.

## Gereksinimler

- **Docker**: [Docker Desktop](https://www.docker.com/products/docker-desktop) yüklü olmalı
- **Docker Compose**: Docker Desktop ile birlikte gelmektedir

## Hızlı Başlangıç

### Windows
```bash
# Development ortamını başlat
docker-start-dev.bat

# Production ortamını başlat
docker-start-prod.bat

# Servisleri durdur
docker-stop.bat

# Logları izle
docker-logs.bat
```

### Linux/macOS
```bash
# Development ortamını başlat
chmod +x docker-start-dev.sh
./docker-start-dev.sh

# Production ortamını başlat
chmod +x docker-start-prod.sh
./docker-start-prod.sh

# Servisleri durdur
chmod +x docker-stop.sh
./docker-stop.sh

# Logları izle
chmod +x docker-logs.sh
./docker-logs.sh
```

## Erişim Noktaları

### Development
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Redis**: localhost:6379
- **MongoDB**: localhost:27017

### Production
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Yapılandırma

### .env Dosyası
Proje root'unda `.env` dosyası kullanılmaktadır. Docker Compose otomatik olarak bu dosyayı yükler.

**Önemli değişkenler:**
- `APP_ENV`: `development` veya `production`
- `DEBUG`: `true` veya `false`
- `ETHEREUM_RPC`: Ethereum RPC endpoint
- `BSC_RPC`: Binance Smart Chain RPC endpoint
- `POLYGON_RPC`: Polygon RPC endpoint
- `MONGODB_URL`: MongoDB bağlantı string'i
- `REDIS_URL`: Redis bağlantı string'i

### Docker Compose Dosyaları

#### docker-compose.yml (Base Configuration)
Tüm servislerin temel konfigürasyonunu içerir.

#### docker-compose.override.yml (Development)
Otomatik olarak yüklenir ve development için override ayarlarını içerir:
- Hot reload etkinleştirilir
- Volume mounts etkinleştirilir
- Debug modunda çalışır

#### docker-compose.prod.yml (Production)
Production için optimize edilmiş ayarları içerir:
- Debug modunda kapalı
- Volume mount'lar azaltılmış
- Performans için optimize edilmiş

## Servisler

### Backend
- **Image**: `python:3.10-slim`
- **Port**: 8000
- **Framework**: FastAPI with Uvicorn
- **Dependencies**: requirements.txt'den yüklenir

### Frontend
- **Image**: `nginx:alpine` (production)
- **Port**: 80 (production) / 5173 (development)
- **Build Tool**: Vite
- **Reverse Proxy**: Nginx (API proxy ile)

### Redis
- **Image**: `redis:7-alpine`
- **Port**: 6379
- **Volume**: `redis_data:/data`

### MongoDB
- **Image**: `mongo:7`
- **Port**: 27017
- **Volume**: `mongodb_data:/data/db`

## Faydalı Docker Commands

### Logları görüntüle
```bash
# Tüm servislerin logları
docker-compose logs -f

# Belirli servisin logları
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f redis
docker-compose logs -f mongodb
```

### Servisleri yönet
```bash
# Tüm servisleri başlat
docker-compose up -d

# Tüm servisleri durdur
docker-compose down

# Spesifik servisi yeniden başlat
docker-compose restart backend

# Servislerin statüsünü kontrol et
docker-compose ps
```

### Images ve containers'ı temizle
```bash
# Kullanılmayan images'ı sil
docker image prune

# Kullanılmayan containers'ı sil
docker container prune

# Tüm Docker kaynaklarını temizle
docker system prune
```

### Backend shell'e eriş
```bash
docker-compose exec backend bash
```

### Frontend shell'e eriş
```bash
docker-compose exec frontend sh
```

### MongoDB'ye eriş
```bash
docker-compose exec mongodb mongosh
```

### Redis'e eriş
```bash
docker-compose exec redis redis-cli
```

## Sorun Giderme

### "Docker daemon is not running"
Docker Desktop'ı başlatın.

### "Port already in use"
Başka bir servis o portu kullanıyor. Port numarasını docker-compose.yml'de değiştirin.

```yaml
ports:
  - "9000:8000"  # Dış port:iç port
```

### "Can't connect to MongoDB"
MongoDB konteynerinin başladığından emin olun:
```bash
docker-compose ps
```

### "Backend can't connect to Redis"
Redis konteynerinin başladığından emin olun:
```bash
docker-compose logs redis
```

### Image derleme hatası
Image'ı yeniden oluşturmayı deneyin:
```bash
docker-compose build --no-cache
```

## Network

Docker Compose otomatik olarak tüm servislerin birbirleriyle iletişim kurabilmesi için bir network oluşturur.

**Service DNS adları:**
- `backend:8000` - Backend servisi
- `frontend` - Frontend servisi
- `redis:6379` - Redis servisi
- `mongodb:27017` - MongoDB servisi

## Volumes

Veriler kalıcı hale getirilmek için volumes kullanılmaktadır:

- `redis_data` - Redis verisi
- `mongodb_data` - MongoDB verisi
- `./backend/data` - Backend veri klasörü (bind mount)
- `./backend/logs` - Backend log dosyaları (bind mount)

## Production Deployment

Production'da docker-compose.prod.yml ile dağıtın:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Önemli noktalar:**
1. `.env` dosyasındaki SECRET_KEY'i değiştirin
2. DEBUG'ı false yapın
3. Production RPC endpoints'leri ayarlayın
4. Reverse proxy (Nginx/HAProxy) ile SSL/TLS sağlayın
5. Database şifrelerini güçlendirin

## Build Optimizasyonu

Frontend Dockerfile multi-stage derleme kullanır:
1. Node stage'de aplikasyon derlenır
2. Derlenen dosyalar Nginx stage'ine kopyalanır
3. Final image boyutu minimum seviyede tutulur

Backend Dockerfile'da da benzer optimizasyonlar yapılmıştır.

## Performans İyileştirmeleri

- Nginx gzip compression etkinleştirilmiş
- Redis persistence yapılandırılmış
- MongoDB volume mounts'ı ayarlanmış
- Statik dosyalar caching ayarlarında 1 yıl expiry

## Kaynaklar

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI with Docker](https://fastapi.tiangolo.com/deployment/docker/)
- [Vite with Docker](https://vitejs.dev/guide/ssr.html#setting-up-the-dev-server)
