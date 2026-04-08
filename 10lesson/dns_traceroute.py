#!/usr/bin/env python3
"""
dns_traceroute.py - Скрипт для выполнения DNS-запросов и traceroute
с сохранением результатов в CSV-файл.

Использование:
    python3 dns_traceroute.py
    python3 dns_traceroute.py --domains example.com,test.com
    python3 dns_traceroute.py --output custom_results.csv
"""

import subprocess
import socket
import csv
import argparse
from datetime import datetime
from typing import List, Tuple, Optional


def get_ip_addresses(domain: str) -> List[str]:
    """
    Выполнить DNS-запрос для домена и вернуть список IP-адресов.
    
    Args:
        domain: Доменное имя для запроса
        
    Returns:
        Список IP-адресов
    """
    try:
        # Используем socket для получения A записей
        addresses = socket.gethostbyname_ex(domain)[2]
        return addresses if addresses else []
    except socket.gaierror as e:
        print(f"⚠️  Ошибка DNS для {domain}: {e}")
        return []
    except Exception as e:
        print(f"⚠️  Неожиданная ошибка для {domain}: {e}")
        return []


def run_traceroute(ip_address: str, max_hops: int = 30, timeout: int = 5) -> List[str]:
    """
    Выполнить traceroute для IP-адреса.
    
    Args:
        ip_address: Целевой IP-адрес
        max_hops: Максимальное количество прыжков
        timeout: Таймаут для каждого прыжка в секундах
        
    Returns:
        Список хопов (маршрутизаторов)
    """
    hops = []
    
    # Определяем доступную утилиту
    traceroute_cmd = None
    if subprocess.run(['which', 'traceroute'], capture_output=True).returncode == 0:
        traceroute_cmd = ['traceroute', '-n', '-m', str(max_hops), '-w', str(timeout)]
    elif subprocess.run(['which', 'tracepath'], capture_output=True).returncode == 0:
        traceroute_cmd = ['tracepath', '-n', '-m', str(max_hops)]
    else:
        # Пробуем использовать ping как fallback (не настоящий traceroute)
        print(f"⚠️  Traceroute/tracepath не найдены, используем альтернативный метод")
        return [f"no_traceroute_available_{ip_address}"]
    
    try:
        result = subprocess.run(
            traceroute_cmd + [ip_address],
            capture_output=True,
            text=True,
            timeout=max_hops * timeout + 10
        )
        
        output = result.stdout + result.stderr
        lines = output.strip().split('\n')
        
        for line in lines:
            # Пропускаем заголовок и пустые строки
            if not line or line.startswith('traceroute') or line.startswith('tracepath'):
                continue
            
            # Извлекаем IP из строки traceroute
            parts = line.split()
            for part in parts:
                # Ищем IP-адреса (простая проверка)
                if '.' in part and ':' not in part:
                    potential_ip = part.rstrip('*')
                    if potential_ip.count('.') == 3:
                        hops.append(potential_ip)
                        break
        
        return hops if hops else ['no_response']
        
    except subprocess.TimeoutExpired:
        return ['timeout']
    except Exception as e:
        return [f'error: {str(e)}']


def process_domains(domains: List[str]) -> List[dict]:
    """
    Обработать список доменов: DNS-запросы и traceroute.
    
    Args:
        domains: Список доменов для обработки
        
    Returns:
        Список словарей с результатами
    """
    results = []
    
    for domain in domains:
        print(f"\n🔍 Обработка домена: {domain}")
        
        # DNS-запрос
        ip_addresses = get_ip_addresses(domain)
        
        if not ip_addresses:
            print(f"  ❌ Не удалось получить IP-адреса для {domain}")
            results.append({
                'domain': domain,
                'ip_address': 'DNS_FAILED',
                'traceroute_hops': 'N/A',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            continue
        
        print(f"  ✓ Найдено IP-адресов: {len(ip_addresses)}")
        
        # Для каждого IP выполняем traceroute
        for ip in ip_addresses:
            print(f"  📡 Traceroute для {ip}...")
            hops = run_traceroute(ip)
            
            # Форматируем хопы в строку
            hops_str = ';'.join(hops) if hops else 'no_hops'
            
            result = {
                'domain': domain,
                'ip_address': ip,
                'traceroute_hops': hops_str,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            results.append(result)
            
            print(f"  ✓ Хопов найдено: {len(hops)}")
    
    return results


def save_to_csv(results: List[dict], filename: str = 'results.csv') -> None:
    """
    Сохранить результаты в CSV-файл.
    
    Args:
        results: Список результатов
        filename: Имя файла для сохранения
    """
    if not results:
        print("⚠️  Нет данных для сохранения")
        return
    
    fieldnames = ['domain', 'ip_address', 'traceroute_hops', 'timestamp']
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\n✅ Результаты сохранены в {filename}")
        print(f"   Всего записей: {len(results)}")
        
    except Exception as e:
        print(f"❌ Ошибка при сохранении: {e}")


def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(
        description='DNS-запросы и traceroute с сохранением в CSV'
    )
    parser.add_argument(
        '--domains', '-d',
        type=str,
        default='google.com,github.com,stackoverflow.com,cloudflare.com,youtube.com',
        help='Список доменов через запятую (по умолчанию: google.com,github.com,stackoverflow.com)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='results.csv',
        help='Имя выходного CSV-файла (по умолчанию: results.csv)'
    )
    
    args = parser.parse_args()
    
    # Парсим список доменов
    domains = [d.strip() for d in args.domains.split(',') if d.strip()]
    
    if not domains:
        print("❌ Не указаны домены для обработки")
        return
    
    print("=" * 60)
    print("DNS-запросы и Traceroute")
    print("=" * 60)
    print(f"Домены: {', '.join(domains)}")
    print(f"Выходной файл: {args.output}")
    print("=" * 60)
    
    # Обработка доменов
    results = process_domains(domains)
    
    # Сохранение в CSV
    save_to_csv(results, args.output)
    
    # Вывод краткой статистики
    print("\n" + "=" * 60)
    print("Краткая статистика:")
    successful = sum(1 for r in results if r['ip_address'] != 'DNS_FAILED')
    print(f"  Успешных: {successful}/{len(results)}")
    print("=" * 60)


if __name__ == '__main__':
    main()
