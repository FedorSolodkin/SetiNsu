# Задание 9: Настройка IPv6 на виртуальных машинах/контейнерах и сравнение пакетов

## Цель
Настроить IPv6 на контейнерах Docker и сравнить структуру пакетов IPv4 и IPv6.

## Требования
- Docker установлен
- Утилиты: `tcpdump`, `ping`, `ping6`

---

## Часть 1: Настройка IPv6 в Docker

### 1.1 Проверка поддержки IPv6
```bash
# Проверить, включен ли IPv6 в Docker
cat /etc/docker/daemon.json

# Если файл пуст или нет настройки IPv6, создаем/редактируем
sudo nano /etc/docker/daemon.json
```

Добавить конфигурацию:
```json
{
    "ipv6": true,
    "fixed-cidr-v6": "2001:db8:1::/64"
}
```

Перезапустить Docker:
```bash
sudo systemctl restart docker
```

### 1.2 Создание сети с поддержкой IPv6
```bash
docker network create --ipv6 --subnet=2001:db8:1::/64 ipv6-network
```

### 1.3 Запуск контейнеров
```bash
# Запустить два контейнера в сети с IPv6
docker run -d --name container1 --network ipv6-network alpine sleep infinity
docker run -d --name container2 --network ipv6-network alpine sleep infinity

# Проверить назначенные адреса
docker exec container1 ip addr show
docker exec container2 ip addr show
```

### 1.4 Тестирование связи
```bash
# Ping по IPv4 (если есть)
docker exec container1 ping -c 3 <IPv4_адрес_container2>

# Ping по IPv6
docker exec container1 ping6 -c 3 <IPv6_адрес_container2>
```

---

## Часть 2: Сравнение пакетов IPv4 и IPv6

### 2.1 Захват пакетов
```bash
# В одном терминале запустить tcpdump
sudo tcpdump -i any -n -vvv 'ip or ip6' -w /tmp/ip_packets.pcap
```

### 2.2 Генерация трафика
```bash
# IPv4 ping
docker exec container1 ping -c 5 8.8.8.8

# IPv6 ping
docker exec container1 ping6 -c 5 2001:4860:4860::8888
```

### 2.3 Анализ пакетов
Остановить tcpdump (Ctrl+C) и проанализировать:
```bash
tcpdump -r /tmp/ip_packets.pcap -nn -vvv
```

### Структура заголовков:

**IPv4 (минимум 20 байт):**
- Version (4 бита)
- IHL (4 бита)
- Type of Service (8 бит)
- Total Length (16 бит)
- Identification (16 бит)
- Flags (3 бита) + Fragment Offset (13 бит)
- TTL (8 бит)
- Protocol (8 бит)
- Header Checksum (16 бит)
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

### Ключевые отличия:
1. **Размер заголовка**: IPv4 - переменный (20-60 байт), IPv6 - фиксированный (40 байт)
2. **Чексумма**: Есть в IPv4, отсутствует в IPv6 (делегирована верхним уровням)
3. **Фрагментация**: В IPv4 - маршрутизаторами, в IPv6 - только источником
4. **Адресация**: 32 бита vs 128 бит
5. **Опции**: В IPv4 - в заголовке, в IPv6 - в расширениях

---

## Автоматизация скриптом

Скрипт для демонстрации: `ipv6_demo.sh`

```bash
#!/bin/bash
# Скрипт демонстрирует настройку IPv6 и захват пакетов

echo "=== Настройка IPv6 в Docker ==="

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "Docker не установлен"
    exit 1
fi

# Создание сети
docker network rm ipv6-network 2>/dev/null
docker network create --ipv6 --subnet=2001:db8:1::/64 ipv6-network

echo "Сеть создана"

# Запуск контейнеров
docker run -d --name ipv6-test1 --network ipv6-network alpine sleep infinity
docker run -d --name ipv6-test2 --network ipv6-network alpine sleep infinity

echo "Контейнеры запущены"

# Получение адресов
IPV6_ADDR=$(docker exec ipv6-test1 ip -6 addr show eth0 | grep inet6 | awk '{print $2}')
echo "IPv6 адрес container1: $IPV6_ADDR"

# Тест связи
echo "Тестирование ping6..."
docker exec ipv6-test1 ping6 -c 3 ipv6-test2

echo "=== Готово ==="
```

---

## Результаты
- [ ] IPv6 настроен в Docker
- [ ] Контейнеры получают IPv6 адреса
- [ ] Связь по IPv6 работает
- [ ] Пакеты захвачены и проанализированы
- [ ] Отличия заголовков задокументированы
