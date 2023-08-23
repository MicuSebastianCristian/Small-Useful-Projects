from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()

# Inițializează WebDriver-ului Remote
driver = webdriver.Remote(
    command_executor='http://127.0.0.1:4444',  # Adresa serverului Selenium
    options=options  # Opțiunile Firefox
)

# ... restul codului tău
