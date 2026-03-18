"""
Модуль для подключения к PostgreSQL и работы с базой данных.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


def get_connection():
    """
    Создаёт и возвращает подключение к PostgreSQL.
    
    Returns:
        psycopg2.connection: Объект подключения к базе данных
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database="postgres",
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "password")
    )


def create_table():
    """
    Создаёт таблицу quotes, если она не существует.
    Запусти один раз при первом запуске.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id SERIAL PRIMARY KEY,
            quote TEXT NOT NULL,
            author VARCHAR(255) NOT NULL,
            tags TEXT,
            author_link VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Таблица quotes создана (или уже существует)")


def save_quote(quote: str, author: str, tags: str, author_link: str) -> int:
    """
    Сохраняет цитату в базу данных.
    
    Args:
        quote: Текст цитаты
        author: Автор цитаты
        tags: Теги (через запятую)
        author_link: Ссылка на автора
        
    Returns:
        int: ID сохранённой записи
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO quotes (quote, author, tags, author_link)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (quote, author, tags, author_link))
    
    result = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    
    return result


def get_all_quotes(limit: int = 100, offset: int = 0) -> list:
    """
    Получает все цитаты из базы данных.
    
    Args:
        limit: Максимальное количество записей
        offset: Пропустить N записей
        
    Returns:
        list: Список словарей с цитатами
    """
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT id, quote, author, tags, author_link, created_at
        FROM quotes
        ORDER BY id DESC
        LIMIT %s OFFSET %s
    """, (limit, offset))
    
    quotes = cursor.fetchall()
    
    # Конвертируем datetime в строку для JSON
    for quote in quotes:
        quote['created_at'] = str(quote['created_at'])
    
    cursor.close()
    conn.close()
    
    return quotes


def get_quote_by_id(quote_id: int) -> dict:
    """
    Получает одну цитату по ID.
    
    Args:
        quote_id: ID цитаты
        
    Returns:
        dict: Словарь с данными цитаты или None
    """
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT id, quote, author, tags, author_link, created_at
        FROM quotes
        WHERE id = %s
    """, (quote_id,))
    
    quote = cursor.fetchone()
    
    if quote:
        quote['created_at'] = str(quote['created_at'])
    
    cursor.close()
    conn.close()
    
    return quote


def delete_quote(quote_id: int) -> bool:
    """
    Удаляет цитату по ID.
    
    Args:
        quote_id: ID цитаты для удаления
        
    Returns:
        bool: True если удалено, False если не найдено
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM quotes WHERE id = %s RETURNING id", (quote_id,))
    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    
    return result is not None


def get_quotes_count() -> int:
    """
    Считает общее количество цитат в базе.
    
    Returns:
        int: Количество записей
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM quotes")
    count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return count