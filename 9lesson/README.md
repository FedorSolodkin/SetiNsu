# Задание 9: Настройка IPv6 на виртуальных машинах/контейнерах и сравнение пакетов

## Цель
Настроить IPv6 на контейнерах Docker и сравнить структуру пакетов IPv4 и IPv6.

## Требования
- Docker Desktop для Windows установлен
- PowerShell (встроен в Windows 10)
- Утилиты: `tcpdump` (в контейнере), `ping`, `ping6`

---

## Часть 1: Настройка IPv6 в Docker на Windows 10

### 1.1 Проверка поддержки IPv6

Docker Desktop для Windows по умолчанию может не иметь включенного IPv6. Для включения:

1. Откройте файл конфигурации Docker (путь зависит от версии):
   - `%PROGRAMDATA%\docker\config\daemon.json`
   
2. Если файл не существует, создайте его и добавьте:
```json
{
    "ipv6": true,
    "fixed-cidr-v6": "2001:db8:1::/64"
}
```

3. Перезапустите Docker Desktop (кликните правой кнопкой на иконке в трее → Quit Docker Desktop, затем запустите снова)

### 1.2 Запуск скрипта автоматизации (PowerShell)

Вместо bash-скрипта используйте PowerShell-версию:

```powershell
# Откройте PowerShell от имени администратора
cd путь\к\папке\9lesson

# Запустите скрипт
powershell -ExecutionPolicy Bypass -File .\ipv6_demo.ps1
```

Или напрямую из PowerShell:
```powershell
.\ipv6_demo.ps1
```

### 1.3 Ручное создание сети с поддержкой IPv6

Если скрипт не работает, выполните команды вручную в PowerShell:

```powershell
# Создание сети с IPv6
docker network create --ipv6 --subnet=2001:db8:1::/64 ipv6-network

# Запуск контейнеров
docker run -d --name container1 --network ipv6-network alpine sleep infinity
docker run -d --name container2 --network ipv6-network alpine sleep infinity

# Проверка адресов
docker exec container1 ip addr show
docker exec container2 ip addr show
```

### 1.4 Тестирование связи

```powershell
# Получение IPv6 адреса второго контейнера
$IPV6 = docker exec container2 ip -6 addr show eth0 | Select-String "inet6" | Where-Object { $_ -notmatch "fe80" }

# Ping по IPv6
docker exec container1 ping6 -c 3 <IPv6_адрес_container2>
```

---

## Часть 2: Сравнение пакетов IPv4 и IPv6

### 2.1 Захват пакетов на Windows

На Windows нет встроенного tcpdump, но можно использовать:

**Вариант 1: Wireshark**
1. Установите Wireshark: https://www.wireshark.org/download.html
2. Запустите захват на интерфейсе Docker (обычно "vEthernet (DockerNAT)" или "eth0" в WSL2)
3. Фильтр: `ipv4 or ipv6`

**Вариант 2: tcpdump в контейнере**
```powershell
# Установите tcpdump в контейнер
docker exec container1 apk add --no-cache tcpdump

# Запустите захват в контейнере
docker exec container1 tcpdump -i eth0 -n -vvv 'ip or ip6'
```

**Вариант 3: Встроенные средства Windows**
```powershell
# Использование NetEventPacketCapture (требует прав администратора)
New-NetEventSession -Name "DockerCapture" -CaptureMode SaveToFile -LocalFilePath "C:\temp\docker_capture.etl"
Add-NetEventNetworkAdapter -Name "vEthernet (DockerNAT)"
Start-NetEventSession
# ... генерируйте трафик ...
Stop-NetEventSession
Remove-NetEventSession -Name "DockerCapture"
```

### 2.2 Генерация трафика

```powershell
# IPv4 ping
docker exec container1 ping -c 5 8.8.8.8

# IPv6 ping
docker exec container1 ping6 -c 5 2001:4860:4860::8888
```

### 2.3 Анализ пакетов

При анализе обращайте внимание на различия:

**IPv4 (минимум 20 байт):**
- Version (4 бита)
- IHL (4 бита)
- Type of Service (8 бит)
- Total Length (16 бит)
- Identification (16 бит)
- Flags (3 бита) + Fragment Offset (13 бит)
- TTL (8 бит)
- Protocol (8 бит)
- Header Checksum (16 бит) ← есть в IPv4
- Source Address (32 бита)
- Destination Address (32 бита)

**IPv6 (40 байт фиксировано):**
- Version (4 бита)
- Traffic Class (8 бит)
- Flow Label (20 бит)
- Payload Length (16 бит)
- Next Header (8 бит)
- Hop Limit (8 бит)
- Source Address (128 бит)
- Destination Address (128 бит)
- Нет Header Checksum ← отсутствует в IPv6
- Нет фрагментации маршрутизаторами

### Ключевые отличия:
1. **Размер заголовка**: IPv4 - переменный (20-60 байт), IPv6 - фиксированный (40 байт)
2. **Чексумма**: Есть в IPv4, отсутствует в IPv6 (делегирована верхним уровням)
3. **Фрагментация**: В IPv4 - маршрутизаторами, в IPv6 - только источником
4. **Адресация**: 32 бита vs 128 бит
5. **Опции**: В IPv4 - в заголовке, в IPv6 - в расширениях

---

## Решение проблем на Windows 10

### Проблема: Docker не поддерживает IPv6
**Решение:** 
1. Убедитесь, что используете Docker Desktop версии 2.0+
2. Проверьте daemon.json
3. Перезапустите Docker Desktop

### Проблема: ping6 не работает
**Решение:**
- Убедитесь, что IPv6 включен в настройках сети Windows
- Попробуйте использовать контейнеры с полным образом (не alpine):
  ```powershell
  docker run -d --name container1 --network ipv6-network ubuntu sleep infinity
  ```

### Проблема: Сеть не создается
**Решение:**
- Запустите PowerShell от имени администратора
- Очистите старые сети: `docker network prune`

---

## Автоматизация скриптом

Скрипт для демонстрации: `ipv6_demo.ps1` (PowerShell версия для Windows)

Запуск:
```powershell
.\ipv6_demo.ps1
```

---

## Результаты
- [ ] IPv6 настроен в Docker на Windows
- [ ] Контейнеры получают IPv6 адреса
- [ ] Связь по IPv6 работает
- [ ] Пакеты захвачены (через Wireshark или tcpdump в контейнере)
- [ ] Отличия заголовков задокументированы
