from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# Lista completă de subdomenii
subdomains = [
    "fiber",
    "vitaminac",
    "keratina",
    "collagen",
    "usa-vitaminc",
    "usa-collagen",
    "usa-keratin",
    "usa-fiber",
    "c-vitamin-hun",
    "rost-hun",
    "keratin-hun",
    "kollagen-hun",
    "vitaminc",
    "liquidcollagen",
    "keratin",
    "liquidfiber"
]

# Opțiuni pentru Firefox
options = webdriver.FirefoxOptions()
options.debugger_address = "localhost:9222"  # Conectează-te la instanța de Firefox deja deschisă

# Conectează-te la sesiunea Firefox deja deschisă
driver = webdriver.Firefox(options=options)

# Așteaptă între 45-60 de secunde pentru a te loga manual și a ajunge pe pagina de DNS-uri
time.sleep(random.randint(45, 60))

# Bucle pentru fiecare subdomeniu
for subdomain in subdomains:
    # Încetinire și "umanoizare" script
    time.sleep(random.uniform(2, 4))

    # Găsește și apasă butonul "Add Record"
    add_record_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
        '//*[@id="react-app"]/div/div/div/div[1]/div/div/main/div/div/div[2]/div[2]/div[2]/div[1]/div/div/div[1]/div/button')))
    add_record_btn.click()
    time.sleep(random.uniform(1, 2))

    # Așteaptă apariția câmpului pentru nume și introdu numele subdomeniului
    name_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="cf-form-input2"]')))
    name_field.clear()
    name_field.send_keys(subdomain)
    time.sleep(random.uniform(1, 2))

    # Așteaptă apariția câmpului pentru IP și introdu IP-ul
    ip_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'content')))
    ip_field.clear()
    ip_field.send_keys("34.202.63.170")
    time.sleep(random.uniform(1, 2))

    # Salvează înregistrarea
    save_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
        '//*[@id="react-app"]/div/div/div/div[1]/div/div/main/div/div/div[2]/div[2]/div[2]/div[1]/form/div[5]/div/button[2]')))
    save_btn.click()

    # Așteaptă ca salvarea să fie efectuată (opțional)
    time.sleep(random.uniform(2, 4))

# Închide browserul
# driver.quit()  # Comentează această linie dacă nu dorești să închizi browserul
