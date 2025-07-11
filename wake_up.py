from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime

STREAMLIT_APPS = [
    "https://your-app-name.streamlit.app"  # ← Replace this
]

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)

for url in STREAMLIT_APPS:
    print(f"Waking up {url}")
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        try:
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'get this app back up')]"))
            )
            button.click()
            print(f"{datetime.datetime.now()} - Woke up {url}")
        except:
            print(f"{datetime.datetime.now()} - App {url} is already running or button not found.")
    except Exception as e:
        print(f"{datetime.datetime.now()} - Failed to load {url}: {e}")

driver.quit()
