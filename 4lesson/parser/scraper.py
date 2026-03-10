import time
import csv
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


URL_LOGIN = "http://quotes.toscrape.com/login"
URL_BASE = "http://quotes.toscrape.com/"
CSV_FILE = "3lesson/parametrs.csv"


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
                url = request['url']
                method = request['method']
                if any(ext in url.lower() for ext in ['.jpg', '.png', '.css', '.ico']):
                    continue
                print(f"{method:6} {url}")
                count += 1
                if count <= 3:
                    headers = request.get('headers', {})
                    if 'Cookie' in headers:
                        print(f"       🍪 Cookie: {headers['Cookie'][:50]}...")
                    if 'User-Agent' in headers:
                        print(f"       🤖 UA: {headers['User-Agent'][:40]}...")
        if count == 0:
            print("   (нет новых запросов)")
        print(f"→ Всего запросов: {count}")
    except Exception as e:
        print(f"   Ошибка чтения логов: {e}")
    print("-" * 70)


options = Options()
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

try:
    print_network_logs(driver, "[ДО ВХОДА]")

    driver.get(URL_LOGIN)
    print_network_logs(driver, "[СТРАНИЦА ЛОГИНА]")

    wait = WebDriverWait(driver, 10)
    username_input = wait.until(EC.visibility_of_element_located((By.ID, "username")))
    password_input = driver.find_element(By.ID, "password")
    login_button = driver.find_element(By.CSS_SELECTOR, "input.btn.btn-primary")

    username_input.send_keys("admin")
    password_input.send_keys("qwerty")

    login_button.click()

    wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Logout")))
    print("успех")

    print_network_logs(driver, "[ПОСЛЕ АВТОРИЗАЦИИ]")

    data_list = []
    page = 1

    while True:
        print(f"страница{page}")

        if page == 1:
            print_network_logs(driver, f"[СТРАНИЦА {page}]")

        quotes = driver.find_elements(By.CLASS_NAME, "quote")
        for quote in quotes:
            text = quote.find_element(By.CLASS_NAME, "text").text
            author = quote.find_element(By.CLASS_NAME, "author").text
            tags = ", ".join([tag.text for tag in quote.find_elements(By.CLASS_NAME, "tag")])
            author_link = quote.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
   
            data_list.append({
                "Цитата": text,
                "Автор": author,
                "Теги": tags,
                "СсылкаАвтора": author_link
            })
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Next"))
            )
            next_button.click()
            page += 1

            if page <= 3:
                print_network_logs(driver, f"[ПЕРЕХОД НА {page}]")

        except:
            print("конец")
            break

    with open(CSV_FILE, 'w') as f:
        fieldnames = ["Цитата", "Автор", "Теги", "СсылкаАвтора"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data_list)

    print_network_logs(driver, "[ФИНАЛ]")

except:
    print(Exception)

finally:
    time.sleep(30)
    driver.quit()