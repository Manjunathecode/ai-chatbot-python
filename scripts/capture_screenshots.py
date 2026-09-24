"""Capture privacy-safe portfolio screenshots from a running local app."""

from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import WebDriverWait


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "screenshots"
BASE_URL = "http://127.0.0.1:5000"


def capture() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--force-device-scale-factor=1")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-first-run")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    try:
        driver.get(BASE_URL)
        wait.until(conditions.visibility_of_element_located((By.ID, "login-page")))
        driver.save_screenshot(str(OUTPUT / "01-demo-entry.png"))

        driver.find_element(By.ID, "name-input").send_keys("Demo User")
        driver.find_element(By.CLASS_NAME, "btn-primary").click()
        wait.until(conditions.visibility_of_element_located((By.ID, "chat-page")))

        message = driver.find_element(By.ID, "msg-input")
        message.send_keys("Where is my order?")
        driver.find_element(By.ID, "send-btn").click()
        wait.until(lambda page: len(page.find_elements(By.CLASS_NAME, "msg-meta")) == 1)
        driver.save_screenshot(str(OUTPUT / "02-order-status.png"))

        driver.find_element(By.CLASS_NAME, "btn-clear").click()
        message = driver.find_element(By.ID, "msg-input")
        message.send_keys("My payment failed")
        driver.find_element(By.ID, "send-btn").click()
        wait.until(lambda page: len(page.find_elements(By.CLASS_NAME, "msg-meta")) == 1)
        driver.save_screenshot(str(OUTPUT / "03-payment-safety.png"))
    finally:
        driver.quit()


if __name__ == "__main__":
    capture()
