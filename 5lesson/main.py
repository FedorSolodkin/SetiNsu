"""
FastAPI приложение для парсинга цитат и работы с базой данных.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Импортируем функции из наших модулей
from database.connection import (
    create_table,
    save_quote,
    get_all_quotes,
    get_quote_by_id,
    delete_quote,
    get_quotes_count
)
from parser.scraper import parse_quotes

# Загружаем переменные окружения
load_dotenv()

# =============================================================================
# LIFESPAN: Инициализация при запуске/остановке (вместо устаревшего on_event)
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Выполняется при запуске и остановке приложения.
    """
    # Код при ЗАПУСКЕ
    print("🚀 Запуск приложения...")
    try:
        create_table()
        print("✅ База данных готова")
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
    
    yield  # Приложение работает здесь
    
    from parser.scraper import cleanup
    cleanup()  # Закрываем Selenium браузер
    # Код при ОСТАНОВКЕ (если нужно)
    print("🛑 Остановка приложения...")

# =============================================================================
# НАСТРОЙКА ПРИЛОЖЕНИЯ
# =============================================================================

app = FastAPI(
    title="Quotes Parser API",
    description="API для парсинга цитат и сохранения в PostgreSQL",
    version="1.0.0",
    lifespan=lifespan  # ← Подключаем lifespan
)

# CORS middleware (разрешаем запросы с других доменов)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production замени на конкретные домены!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
def root():
    """
    Корневая точка — проверка работоспособности API.
    """
    return {
        "message": "Quotes Parser API работает!",
        "docs": "http://127.0.0.1:8000/docs",
        "endpoints": {
            "parse": "/parse?url=<URL>",
            "get_data": "/get_data?limit=100&offset=0",
            "get_data_by_id": "/get_data/{id}",
            "delete": "/delete_data/{id}"
        }
    }


@app.get("/parse")
def parse_url(
    url: str = Query(..., description="URL страницы для парсинга"),
    save_to_db: bool = Query(True, description="Сохранять ли в БД")
):
    """
    Endpoint 1: Парсит страницу и сохраняет результат в БД.
    
    Пример:
        curl "http://127.0.0.1:8000/parse?url=https://quotes.toscrape.com/page/1/"
    """
    # Валидация URL
    if not url.startswith(('http://', 'https://')):
        raise HTTPException(
            status_code=400,
            detail="URL должен начинаться с http:// или https://"
        )
    
    try:
        # 1. Парсим страницу
        parsed_data = parse_quotes(url)
        
        # 2. Сохраняем в БД (если нужно)
        quote_id = None
        if save_to_db:
            quote_id = save_quote(
                quote=parsed_data["quote"],
                author=parsed_data["author"],
                tags=parsed_data["tags"],
                author_link=parsed_data["author_link"]
            )
        
        # 3. Возвращаем результат
        response = {
            "status": "success",
            "message": "Страница успешно спарсена",
            "data": parsed_data
        }
        
        if quote_id:
            response["saved_to_db"] = True
            response["id"] = quote_id
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка: {str(e)}")


@app.get("/get_data")
def get_data(
    limit: int = Query(100, ge=1, le=1000, description="Максимум записей"),
    offset: int = Query(0, ge=0, description="Пропустить N записей")
):
    """
    Endpoint 2: Получает все цитаты из базы данных.
    
    Пример:
        curl "http://127.0.0.1:8000/get_data?limit=10&offset=0"
    """
    try:
        quotes = get_all_quotes(limit=limit, offset=offset)
        total = get_quotes_count()
        
        return {
            "status": "success",
            "count": len(quotes),
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": quotes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения данных: {str(e)}")


@app.get("/get_data/{quote_id}")
def get_data_by_id(quote_id: int):
    """
    Endpoint 3: Получает одну цитату по ID.
    
    Пример:
        curl "http://127.0.0.1:8000/get_data/1"
    """
    try:
        quote = get_quote_by_id(quote_id)
        
        if not quote:
            raise HTTPException(status_code=404, detail="Цитата не найдена")
        
        return {
            "status": "success",
            "data": quote
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@app.delete("/delete_data/{quote_id}")
def delete_data(quote_id: int):
    """
    Endpoint 4: Удаляет цитату по ID.
    
    Пример:
        curl -X DELETE "http://127.0.0.1:8000/delete_data/1"
    """
    try:
        success = delete_quote(quote_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Цитата не найдена")
        
        return {
            "status": "success",
            "message": f"Цитата {quote_id} удалена"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@app.get("/stats")
def get_stats():
    """
    Endpoint 5: Статистика базы данных.
    """
    try:
        return {
            "status": "success",
            "total_quotes": get_quotes_count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")

# =============================================================================
# ЗАПУСК СЕРВЕРА
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8001"))
    
    print(f"🚀 Запуск сервера на {host}:{port}")
    print(f"📚 Документация: http://{host}:{port}/docs")
    print(f"💡 Для автоперезагрузки используй: uvicorn main:app --reload")
    
    # reload=False при запуске через python main.py
    # Для reload=True запускай через терминал: uvicorn main:app --reload
    uvicorn.run("main:app", host=host, port=port, reload=False)