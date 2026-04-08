# Задание 10: DNS-запросы и traceroute с сохранением в CSV

## Цель
Выполнить DNS-запросы для списка доменов, получить IP-адреса, выполнить traceroute и сохранить результаты в CSV-файл.

## Требования
- Python 3.x
- Утилиты: `dig` или `nslookup`, `traceroute` или `tracepath`

---

## Часть 1: Ручное выполнение в терминале

### 1.1 DNS-запросы
```bash
# Для каждого домена выполнить DNS-запрос
dig google.com +short
dig github.com +short
dig stackoverflow.com +short

# Или использовать nslookup
nslookup google.com
nslookup github.com
```

### 1.2 Traceroute
```bash
# Для каждого полученного IP выполнить traceroute
traceroute -n 142.250.180.78  # google.com
traceroute -n 140.82.121.4   # github.com
traceroute -n 151.101.1.69   # stackoverflow.com

# Если traceroute нет, использовать tracepath
tracepath -n 142.250.180.78
```

### 1.3 Сохранение результатов вручную
```bash
# Создать CSV файл
echo "domain,ip_address,traceroute_hops" > results.csv

# Пример добавления строки (упрощенно)
echo "google.com,142.250.180.78,\"192.168.1.1 10.0.0.1 142.250.180.78\"" >> results.csv
```

---

## Часть 2: Автоматизация скриптом на Python

Скрипт: `dns_traceroute.py`

### Возможности:
- DNS-запросы для списка доменов
- Получение всех IP-адресов (A записи)
- Выполнение traceroute для каждого IP
- Сохранение результатов в CSV
- Обработка ошибок и таймаутов

### Запуск:
```bash
python3 dns_traceroute.py
```

Или с кастомным списком доменов:
```bash
python3 dns_traceroute.py --domains example.com,test.com
```

---

## Структура CSV-файла

| domain | ip_address | traceroute_hops | timestamp |
|--------|-----------|-----------------|-----------|
| google.com | 142.250.180.78 | 192.168.1.1;10.0.0.1;... | 2024-01-01 12:00:00 |

---

## Результаты
- [ ] DNS-запросы выполнены вручную
- [ ] Traceroute выполнен вручную
- [ ] Скрипт на Python создан
- [ ] Результаты сохранены в CSV
- [ ] Файл results.csv содержит корректные данные
