# Задание 10: DNS-запросы и traceroute с сохранением в CSV

## Цель
Выполнить DNS-запросы для списка доменов, получить IP-адреса, выполнить traceroute и сохранить результаты в CSV-файл.

## Требования
- Python 3.x (доступен на Windows 10)
- Утилиты: `tracert` (встроена в Windows) или `traceroute` (Linux/macOS)

---

## Часть 1: Ручное выполнение в терминале (Windows 10)

### 1.1 DNS-запросы

На Windows используйте встроенную утилиту `nslookup`:

```cmd
REM Для каждого домена выполнить DNS-запрос
nslookup google.com
nslookup github.com
nslookup stackoverflow.com
```

Или через PowerShell:
```powershell
Resolve-DnsName google.com
Resolve-DnsName github.com
Resolve-DnsName stackoverflow.com
```

### 1.2 Traceroute

На Windows используется команда `tracert` (встроена в систему):

```cmd
REM Для каждого полученного IP выполнить traceroute
tracert -d 142.250.180.78  REM google.com
tracert -d 140.82.121.4   REM github.com
tracert -d 151.101.1.69   REM stackoverflow.com
```

Или в PowerShell:
```powershell
tracert -d 142.250.180.78
```

### 1.3 Сохранение результатов вручную

Создайте CSV файл в PowerShell:
```powershell
# Создать CSV файл
"domain,ip_address,traceroute_hops" | Out-File -FilePath results.csv -Encoding UTF8

# Пример добавления строки
"google.com,142.250.180.78,""192.168.1.1;10.0.0.1;142.250.180.78""" | Out-File -FilePath results.csv -Append -Encoding UTF8
```

---

## Часть 2: Автоматизация скриптом на Python

Скрипт: `dns_traceroute.py`

### Возможности:
- ✅ Кроссплатформенность: работает на Windows 10, Linux и macOS
- ✅ Автоматическое определение ОС и выбор утилиты (tracert/traceroute)
- ✅ DNS-запросы для списка доменов
- ✅ Получение всех IP-адресов (A записи)
- ✅ Выполнение traceroute для каждого IP
- ✅ Сохранение результатов в CSV
- ✅ Обработка ошибок и таймаутов

### Запуск на Windows 10:

```cmd
REM Откройте Command Prompt или PowerShell
cd путь\к\папке\10lesson

REM Запустите скрипт
python dns_traceroute.py
```

Или с кастомным списком доменов:
```cmd
python dns_traceroute.py --domains example.com,test.com
python dns_traceroute.py --output custom_results.csv
```

### Примечания для Windows:
- Скрипт автоматически определяет Windows и использует `tracert` вместо `traceroute`
- Таймауты адаптированы для Windows (tracert использует миллисекунды)
- Парсинг вывода учитывает формат tracetrt

---

## Структура CSV-файла

| domain | ip_address | traceroute_hops | timestamp |
|--------|-----------|-----------------|-----------|
| google.com | 142.250.180.78 | 192.168.1.1;10.0.0.1;... | 2024-01-01 12:00:00 |

---

## Решение проблем на Windows 10

### Проблема: Python не найден
**Решение:**
1. Установите Python с https://www.python.org/downloads/
2. При установке отметьте галочку "Add Python to PATH"
3. Перезапустите терминал

### Проблема: tracert не работает
**Решение:**
- Убедитесь, что брандмауэр не блокирует ICMP-запросы
- Попробуйте запустить от имени администратора
- Некоторые сети могут блокировать traceroute

### Проблема: DNS не разрешается
**Решение:**
- Проверьте подключение к интернету
- Попробуйте использовать публичные DNS (8.8.8.8, 1.1.1.1)
- Проверьте настройки сетевого адаптера

---

## Результаты
- [ ] DNS-запросы выполнены вручную (через nslookup или Resolve-DnsName)
- [ ] Traceroute выполнен вручную (через tracert)
- [ ] Скрипт на Python запущен на Windows
- [ ] Результаты сохранены в CSV
- [ ] Файл results.csv содержит корректные данные
