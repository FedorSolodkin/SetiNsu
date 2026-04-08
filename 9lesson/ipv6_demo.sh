#!/bin/bash
# ipv6_demo.sh - Скрипт для демонстрации настройки IPv6 в Docker

set -e

echo "=== Настройка IPv6 в Docker ==="

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен"
    exit 1
fi

echo "✓ Docker найден"

# Проверка прав
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Требуется sudo для некоторых операций"
fi

# Очистка старых контейнеров и сетей
echo "Очистка старых ресурсов..."
docker rm -f ipv6-test1 ipv6-test2 2>/dev/null || true
docker network rm ipv6-network 2>/dev/null || true

# Создание сети с IPv6
echo "Создание сети с поддержкой IPv6..."
docker network create --ipv6 --subnet=2001:db8:1::/64 ipv6-network

echo "✓ Сеть создана"

# Запуск контейнеров
echo "Запуск контейнеров..."
docker run -d --name ipv6-test1 --network ipv6-network alpine sleep infinity
docker run -d --name ipv6-test2 --network ipv6-network alpine sleep infinity

echo "✓ Контейнеры запущены"

# Получение и отображение адресов
echo ""
echo "=== Адреса контейнеров ==="
echo "Container 1:"
docker exec ipv6-test1 ip addr show eth0 | grep inet
echo ""
echo "Container 2:"
docker exec ipv6-test2 ip addr show eth0 | grep inet

# Тестирование связи
echo ""
echo "=== Тестирование связи ==="
IPV6_ADDR=$(docker exec ipv6-test2 ip -6 addr show eth0 | grep inet6 | grep -v fe80 | awk '{print $2}' | cut -d'/' -f1)
echo "IPv6 адрес container2: $IPV6_ADDR"

echo "Ping6 от container1 к container2:"
docker exec ipv6-test1 ping6 -c 3 "$IPV6_ADDR" || echo "⚠️  Ping6 не удался (возможно, нужен дополнительный конфиг)"

echo ""
echo "=== Сравнение заголовков ==="
echo "IPv4 заголовок: минимум 20 байт, есть checksum, фрагментация маршрутизаторами"
echo "IPv6 заголовок: 40 байт фиксировано, нет checksum, фрагментация только источником"
echo "IPv4 адреса: 32 бита (4 байта), пример: 192.168.1.1"
echo "IPv6 адреса: 128 бит (16 байт), пример: 2001:db8:1::1"

echo ""
echo "=== Для захвата пакетов выполните: ==="
echo "sudo tcpdump -i any -n -vvv 'ip or ip6' -w /tmp/ip_packets.pcap"
echo "# В другом терминале:"
echo "docker exec ipv6-test1 ping6 -c 5 $IPV6_ADDR"
echo "# Затем анализируйте: tcpdump -r /tmp/ip_packets.pcap -nn -vvv"

echo ""
echo "=== Готово ==="
