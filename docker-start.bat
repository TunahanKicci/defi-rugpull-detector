@echo off
REM Docker başlatma betiği - Development ortamı (Windows)

echo ==================================================
echo DeFi Rug Pull Detector - Docker Development
echo ==================================================
echo.

REM Docker kontrolü
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker yüklü değil. Lütfen Docker Desktop yükleyin.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose yüklü değil.
    pause
    exit /b 1
)

echo ✅ Docker kurulu
echo.
echo 📦 Docker images oluşturuluyor...
docker-compose build

echo.
echo 🚀 Servisleri başlatıyor...
docker-compose up -d

echo.
echo ==================================================
echo ✅ Başlatma tamamlandı!
echo ==================================================
echo.
echo 📍 Frontend:   http://localhost:5173
echo 📍 Backend:    http://localhost:8000
echo 📍 API Docs:   http://localhost:8000/docs
echo.
echo Logları görmek için:
echo   docker-compose logs -f
echo.
echo Belirli servisi görmek için:
echo   docker-compose logs -f [service-name]
echo.
echo Servisleri durdurmak için:
echo   docker-compose down
echo.
pause
