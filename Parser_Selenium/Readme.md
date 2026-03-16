Quotes Scraper - Парсер цитат

ОПИСАНИЕ:
Парсер сайта quotes.toscrape.com с авторизацией.
Собирает цитаты, авторов, теги и сохраняет в CSV.

ТРЕБОВАНИЯ:
- Python 3.8+
- pip install selenium webdriver-manager
- Google Chrome

УСТАНОВКА:
1. Сделайте git clone https://github.com/FedorSolodkin/SetiNsu/tree/main/Parser_Selenium: 
4. Установите зависимости:
   pip install selenium webdriver-manager

ЗАПУСК:
   python main.py

ЧТО ДЕЛАЕТ СКРИПТ:
1. Открывает браузер Chrome
2. Заходит на страницу логина
3. Вводит admin / qwerty
4. Парсит цитаты со всех страниц
5. Сохраняет в 3lesson/parametrs.csv
6. Показывает сетевые запросы в консоли

РЕЗУЛЬТАТ:
Файл Parser_Selenium/parametrs.csv с колонками:
- Цитата
- Автор
- Теги
- СсылкаАвтора
