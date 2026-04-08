# ipv6_demo.ps1 - Скрипт для демонстрации настройки IPv6 в Docker (Windows 10)
# Запуск: powershell -ExecutionPolicy Bypass -File .\ipv6_demo.ps1

Write-Host "=== Настройка IPv6 в Docker (Windows 10) ===" -ForegroundColor Cyan

# Проверка Docker
try {
    $dockerVersion = docker --version 2>$null
    if (-not $dockerVersion) {
        Write-Host "❌ Docker не установлен или не найден в PATH" -ForegroundColor Red
        Write-Host "Установите Docker Desktop для Windows: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✓ Docker найден: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка проверки Docker: $_" -ForegroundColor Red
    exit 1
}

# Очистка старых контейнеров и сетей
Write-Host "`nОчистка старых ресурсов..." -ForegroundColor Cyan
docker rm -f ipv6-test1 ipv6-test2 2>$null | Out-Null
docker network rm ipv6-network 2>$null | Out-Null

# Создание сети с IPv6
Write-Host "Создание сети с поддержкой IPv6..." -ForegroundColor Cyan
try {
    docker network create --ipv6 --subnet=2001:db8:1::/64 ipv6-network 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Сеть создана" -ForegroundColor Green
    } else {
        # Сеть может уже существовать
        Write-Host "⚠️  Сеть уже существует или создана с предупреждениями" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Предупреждение при создании сети: $_" -ForegroundColor Yellow
}

# Запуск контейнеров
Write-Host "`nЗапуск контейнеров..." -ForegroundColor Cyan
try {
    docker run -d --name ipv6-test1 --network ipv6-network alpine sleep infinity 2>$null
    docker run -d --name ipv6-test2 --network ipv6-network alpine sleep infinity 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Контейнеры запущены" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Контейнеры запущены с предупреждениями" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Ошибка запуска контейнеров: $_" -ForegroundColor Red
}

# Небольшая задержка для инициализации
Start-Sleep -Seconds 3

# Получение и отображение адресов
Write-Host "`n=== Адреса контейнеров ===" -ForegroundColor Cyan
Write-Host "Container 1:" -ForegroundColor White
docker exec ipv6-test1 ip addr show eth0 2>$null | Select-String "inet"

Write-Host "`nContainer 2:" -ForegroundColor White
docker exec ipv6-test2 ip addr show eth0 2>$null | Select-String "inet"

# Тестирование связи
Write-Host "`n=== Тестирование связи ===" -ForegroundColor Cyan
$ipv6Info = docker exec ipv6-test2 ip -6 addr show eth0 2>$null | Select-String "inet6" | Where-Object { $_ -notmatch "fe80" }
if ($ipv6Info) {
    $ipv6Addr = ($ipv6Info -split '\s+')[1] -split '/' | Select-Object -First 1
    Write-Host "IPv6 адрес container2: $ipv6Addr" -ForegroundColor White
    
    Write-Host "`nPing6 от container1 к container2:" -ForegroundColor White
    docker exec ipv6-test1 ping6 -c 3 "$ipv6Addr" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Ping6 не удался (возможно, нужна дополнительная настройка IPv6 в Docker)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Не удалось получить IPv6 адрес" -ForegroundColor Yellow
}

Write-Host "`n=== Сравнение заголовков ===" -ForegroundColor Cyan
Write-Host "IPv4 заголовок: минимум 20 байт, есть checksum, фрагментация маршрутизаторами" -ForegroundColor White
Write-Host "IPv6 заголовок: 40 байт фиксировано, нет checksum, фрагментация только источником" -ForegroundColor White
Write-Host "IPv4 адреса: 32 бита (4 байта), пример: 192.168.1.1" -ForegroundColor White
Write-Host "IPv6 адреса: 128 бит (16 байт), пример: 2001:db8:1::1" -ForegroundColor White

Write-Host "`n=== Для захвата пакетов выполните (в Wireshark или tcpdump): ===" -ForegroundColor Cyan
Write-Host "# В Docker Desktop можно использовать встроенный мониторинг сети" -ForegroundColor White
Write-Host "# Или установите tcpdump в контейнер:" -ForegroundColor White
Write-Host "docker exec ipv6-test1 apk add --no-cache tcpdump" -ForegroundColor Gray
Write-Host "docker exec ipv6-test1 tcpdump -i eth0 -n -vvv 'ip or ip6'" -ForegroundColor Gray
Write-Host ""
Write-Host "# Альтернативно используйте Wireshark на хосте для анализа трафика" -ForegroundColor White

Write-Host "`n=== Готово ===" -ForegroundColor Green
Write-Host "`nПримечание для Windows 10:" -ForegroundColor Yellow
Write-Host "- Убедитесь, что Docker Desktop настроен на использование WSL 2 или Hyper-V" -ForegroundColor White
Write-Host "- Для полноценной поддержки IPv6 может потребоваться настройка daemon.json" -ForegroundColor White
Write-Host "- Пример daemon.json для Windows (путь: %PROGRAMDATA%\docker\config\daemon.json):" -ForegroundColor White
Write-Host '{' -ForegroundColor Gray
Write-Host '  "ipv6": true,' -ForegroundColor Gray
Write-Host '  "fixed-cidr-v6": "2001:db8:1::/64"' -ForegroundColor Gray
Write-Host '}' -ForegroundColor Gray
