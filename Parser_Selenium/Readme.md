🕷️ Quotes Scraper (Selenium)
Парсер сайта quotes.toscrape.com с авторизацией, сбором цитат и логированием сетевых запросов.
⚠️ Учебный проект — предназначен для изучения Selenium, работы с сетевыми логами и парсинга динамических страниц.
✨ Возможности
🔐 Авторизация на сайте через Selenium
📄 Парсинг цитат: текст, автор, теги, ссылка на автора
🔄 Пагинация: автоматический переход по страницам
🌐 Логирование сетевых запросов: просмотр методов, URL, Cookie, User-Agent
💾 Экспорт в CSV: сохранение данных в удобном формате
🛡️ Обработка ошибок: try/except блоки для стабильной работы
🛠 Требования
Компонент
Версия
Python
3.8+
Selenium
4.x
Chrome
114+
ChromeDriver
Автоустановка через webdriver-manager
📦 Установка
1. Клонируйте репозиторий (или скопируйте файл)
bash
12
git clone https://github.com/FedorSolodkin/SetiNsu/Parser_Selenium
cd Parser_Selenium
2. Создайте виртуальное окружение (рекомендуется)
bash
12345
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
3. Установите зависимости
bash
1
pip install selenium webdriver-manager
4. Создайте папку для вывода (если нужно)
bash
1
🚀 Использование
Быстрый запуск
bash
1
Что произойдёт:
🌐 Откроется Chrome в автоматическом режиме
🔐 Скрипт войдёт под admin / qwerty
📊 Соберёт цитаты со всех страниц
📄 Сохранит данные в 3lesson/parametrs.csv
🧹 Закроет браузер через 30 секунд после завершения
