@echo off
REM Docker loglarını gösterme (Windows)

if "%1"=="" (
    echo 🔍 Tüm servislerin logları...
    docker-compose logs -f
) else (
    echo 🔍 %1 servisi logları...
    docker-compose logs -f %1
)
