"""
Твой рабочий парсер + защита от ошибок (None, split, etc.)
"""
import time
import csv
import json
import psycopg2
from typing import Dict, List
from dotenv import load_dotenv
import os

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

load_dotenv()

# ============================================================================
# КОНСТАНТЫ
# ============================================================================

URL_LOGIN = "http://quotes.toscrape.com/login"
URL_BASE = "http://quotes.toscrape.com/"
CSV_FILE = "parser/parameters.csv"

# ============================================================================
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ
# ============================================================================

def print_network_logs(driver, label=""):
    print(f"\n🌐 {label} Сетевые запросы:")
    print("-" * 70)
    try:
        logs = driver.get_log('performance')
        count = 0
        for entry in logs:
            message = json.loads(entry['message'])['message']
            if message['method'] == 'Network.requestWillBeSent':
                request = message['params']['request']
                url_log = request['url']
                method = request['method']
                if any(ext in url_log.lower() for ext in ['.jpg', '.png', '.css', '.ico']):
                    continue
                print(f"{method:6} {url_log}")
                count += 1
        if count == 0:
            print("   (нет новых запросов)")
        print(f"→ Всего запросов: {count}")
    except Exception as e:
        print(f"   Ошибка чтения логов: {e}")
    print("-" * 70)

# ============================================================================
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
# ============================================================================

_driver: webdriver.Chrome = None
_is_logged_in: bool = False

def _get_driver() -> webdriver.Chrome:
    global _driver
    if _driver is None:
        options = Options()
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--headless")  # Раскомментируй если нужно
        
        _driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
    return _driver

def _login(driver):
    global _is_logged_in
    if _is_logged_in:
        return
    
    driver.get(URL_LOGIN)
    
    wait = WebDriverWait(driver, 10)
    username_input = wait.until(EC.visibility_of_element_located((By.ID, "username")))
    password_input = driver.find_element(By.ID, "password")
    login_button = driver.find_element(By.CSS_SELECTOR, "input.btn.btn-primary")

    username_input.send_keys("admin")
    password_input.send_keys("qwerty")
    login_button.click()

    wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Logout")))
    _is_logged_in = True
    print("✅ Авторизация успешна")

# ============================================================================
# ОСНОВНАЯ ФУНКЦИЯ ПАРСИНГА (с защитой от None)
# ============================================================================

def parse_quotes(url: str) -> Dict:
    """Парсит страницу и возвращает первую цитату с максимальной защитой."""
    global _is_logged_in
    
    driver = _get_driver()
    
    if not _is_logged_in:
        _login(driver)
    
    try:
        driver.get(url)
        time.sleep(2)
        
        quotes = driver.find_elements(By.CLASS_NAME, "quote")
        if not quotes:
            raise ValueError(f"Не найдено цитат на странице {url}")
        
        quote_element = quotes[0]
        
        # === Безопасные хелперы для извлечения ===
        
        def safe_text(parent, by, value):
            """Возвращает текст элемента или пустую строку."""
            try:
                elem = parent.find_element(by, value)
                return str(elem.text).strip() if elem and elem.text else ""
            except (NoSuchElementException, Exception):
                return ""
        
        def safe_attr(parent, css_selector, attr_name):
            """Возвращает атрибут элемента или пустую строку."""
            try:
                elem = parent.find_element(By.CSS_SELECTOR, css_selector)
                val = elem.get_attribute(attr_name) if elem else None
                return str(val).strip() if val else ""
            except (NoSuchElementException, Exception):
                return ""
        
        def safe_tags_list(parent, class_name):
            """Возвращает строку тегов через запятую."""
            try:
                elems = parent.find_elements(By.CLASS_NAME, class_name)
                texts = [str(e.text).strip() for e in elems if e and e.text]
                return ", ".join([t for t in texts if t])
            except Exception:
                return ""
        
        # === Извлекаем данные ===
        text = safe_text(quote_element, By.CLASS_NAME, "text")
        author = safe_text(quote_element, By.CLASS_NAME, "author")
        tags = safe_tags_list(quote_element, "tag")
        author_link = safe_attr(quote_element, "a[href*='/author/']", "href")
        
        # === Финальная гарантия: НИЧЕГО не может быть None ===
        result = {
            "quote": text if text else "",
            "author": author if author else "",
            "tags": tags if tags else "",
            "author_link": author_link if author_link else ""
        }
        
        # Дополнительная страховка (на всякий случай)
        for key in result:
            if result[key] is None:
                result[key] = ""
            elif not isinstance(result[key], str):
                result[key] = str(result[key])
        
        return result
        
    except Exception as e:
        import traceback
        print(f"❌ Ошибка парсинга: {type(e).__name__}: {e}")
        traceback.print_exc()  # ← теперь будет видно в docker logs!
        raise RuntimeError(f"Ошибка парсинга: {str(e)}")

# ============================================================================
# СОХРАНЕНИЕ ВСЕХ ЦИТАТ В БД
# ============================================================================

def _save_all_to_db(data_list: List[Dict]):
    """Сохраняет все цитаты в PostgreSQL с защитой от ошибок."""
    if not data_list:
        print("⚠️ Нет данных для сохранения в БД")
        return
    
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "quotes-dbb"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "mysecretpassword")
        )
        cursor = conn.cursor()
        
        saved_count = 0
        for item in data_list:
            try:
                # Гарантия что все значения — строки (не None!)
                quote = str(item.get("Цитата") or "")
                author = str(item.get("Автор") or "")
                tags = str(item.get("Теги") or "")
                author_link = str(item.get("СсылкаАвтора") or "")
                
                cursor.execute("""
                    INSERT INTO quotes (quote, author, tags, author_link)
                    VALUES (%s, %s, %s, %s)
                """, (quote, author, tags, author_link))
                saved_count += 1
            except Exception as e:
                print(f"⚠️ Не сохранена цитата: {e}")
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Сохранено {saved_count} цитат в базу данных")
        
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")

# ============================================================================
# ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================

def parse_all_quotes(max_pages: int = 10) -> List[Dict]:
    """Парсит все страницы и возвращает список цитат."""
    global _is_logged_in
    
    driver = _get_driver()
    if not _is_logged_in:
        _login(driver)
    
    data_list = []
    page = 1
    current_url = URL_BASE

    while page <= max_pages:
        print(f"📄 Страница {page}")
        
        driver.get(current_url)
        time.sleep(1)
        
        quotes = driver.find_elements(By.CLASS_NAME, "quote")
        for quote in quotes:
            try:
                text_elem = quote.find_element(By.CLASS_NAME, "text")
                author_elem = quote.find_element(By.CLASS_NAME, "author")
                tag_elems = quote.find_elements(By.CLASS_NAME, "tag")
                link_elem = quote.find_element(By.CSS_SELECTOR, "a[href*='/author/']")
                
                data_list.append({
                    "Цитата": text_elem.text.strip() if text_elem else "",
                    "Автор": author_elem.text.strip() if author_elem else "",
                    "Теги": ", ".join([t.text.strip() for t in tag_elems if t and t.text]) if tag_elems else "",
                    "СсылкаАвтора": link_elem.get_attribute("href") if link_elem else ""
                })
            except:
                continue
        
        try:
            next_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Next"))
            )
            current_url = next_button.get_attribute("href")
            page += 1
        except:
            break
    
    return data_list

def save_to_csv(data_list: List[Dict], filename: str = None):
    """Сохраняет данные в CSV."""
    if filename is None:
        filename = CSV_FILE
    if not data_list:
        return
        
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["Цитата", "Автор", "Теги", "СсылкаАвтора"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in data_list:
            writer.writerow({
                "Цитата": str(item.get("Цитата") or ""),
                "Автор": str(item.get("Автор") or ""),
                "Теги": str(item.get("Теги") or ""),
                "СсылкаАвтора": str(item.get("СсылкаАвтора") or "")
            })
    print(f"✅ Сохранено {len(data_list)} записей в {filename}")

def cleanup():
    """Закрывает браузер."""
    global _driver, _is_logged_in
    if _driver:
        print("🔚 Закрытие браузера...")
        time.sleep(2)
        _driver.quit()
        _driver = None
        _is_logged_in = False

# ============================================================================
# ДЛЯ ЗАПУСКА В ДОКЕРЕ: инициализация БД при старте
# ============================================================================

def init_db():
    """Создаёт таблицу если не существует (для Docker)."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "quotes-db"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "mysecretpassword")
        )
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
        print("✅ Таблица quotes готова")
    except Exception as e:
        print(f"⚠️ Ошибка инициализации БД: {e}")

# ============================================================================
# MAIN ДЛЯ ТЕСТИРОВАНИЯ
# ============================================================================

if __name__ == "__main__":
    try:
        print("🧪 Тестирование парсера...")
        init_db()
        result = parse_quotes("http://quotes.toscrape.com/page/1/")
        print(f"\n✅ Результат:")
        for k, v in result.items():
            print(f"   {k}: {v[:50] if len(str(v)) > 50 else v}")
    finally:
        cleanup()