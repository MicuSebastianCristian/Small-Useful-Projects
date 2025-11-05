from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import sys

# ANSI Color Codes for beautiful terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner():
    """Print a beautiful banner for the application"""
    banner = f"""
{Colors.OKCYAN}{'═' * 70}
{Colors.BOLD}    ☁️  CLOUDFLARE DNS AUTOMATION TOOL ☁️{Colors.ENDC}
{Colors.OKCYAN}{'═' * 70}{Colors.ENDC}
"""
    print(banner)

def print_progress_bar(current, total, subdomain):
    """Display a progress bar"""
    percent = (current / total) * 100
    filled = int(percent / 2)
    bar = '█' * filled + '░' * (50 - filled)
    print(f"\r{Colors.OKBLUE}Progress: [{bar}] {percent:.1f}% - {subdomain}{Colors.ENDC}", end='', flush=True)

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

print_banner()
print(f"{Colors.WARNING}📋 Total subdomenii de procesat: {len(subdomains)}{Colors.ENDC}\n")

# Opțiuni pentru Firefox
options = webdriver.FirefoxOptions()
options.debugger_address = "localhost:9222"  # Conectează-te la instanța de Firefox deja deschisă

print(f"{Colors.OKCYAN}🔌 Conectare la Firefox...{Colors.ENDC}")
try:
    driver = webdriver.Firefox(options=options)
    print(f"{Colors.OKGREEN}✓ Conectat cu succes!{Colors.ENDC}\n")
except Exception as e:
    print(f"{Colors.FAIL}✗ Eroare la conectare: {e}{Colors.ENDC}")
    sys.exit(1)

# Așteaptă între 45-60 de secunde pentru a te loga manual și a ajunge pe pagina de DNS-uri
wait_time = random.randint(45, 60)
print(f"{Colors.WARNING}⏳ Așteptare {wait_time} secunde pentru autentificare manuală...{Colors.ENDC}")
for i in range(wait_time):
    remaining = wait_time - i
    print(f"\r{Colors.OKCYAN}Timp rămas: {remaining}s{Colors.ENDC}", end='', flush=True)
    time.sleep(1)
print(f"\n{Colors.OKGREEN}✓ Timp de așteptare expirat. Începem procesarea DNS-urilor...{Colors.ENDC}\n")

# Bucle pentru fiecare subdomeniu
succes_count = 0
error_count = 0
total = len(subdomains)

print(f"{Colors.OKCYAN}{'═' * 70}{Colors.ENDC}\n")

for index, subdomain in enumerate(subdomains, 1):
    try:
        print(f"\n{Colors.BOLD}[{index}/{total}] Procesare: {subdomain}{Colors.ENDC}")

        # Încetinire și "umanoizare" script
        delay = random.uniform(2, 4)
        print(f"{Colors.OKCYAN}  ⏱️  Delay: {delay:.1f}s{Colors.ENDC}")
        time.sleep(delay)

        # Găsește și apasă butonul "Add Record"
        print(f"{Colors.OKCYAN}  🔘 Click pe 'Add Record'...{Colors.ENDC}")
        add_record_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
            '//*[@id="react-app"]/div/div/div/div[1]/div/div/main/div/div/div[2]/div[2]/div[2]/div[1]/div/div/div[1]/div/button')))
        add_record_btn.click()
        time.sleep(random.uniform(1, 2))

        # Așteaptă apariția câmpului pentru nume și introdu numele subdomeniului
        print(f"{Colors.OKCYAN}  📝 Introducere nume subdomeniu: {subdomain}{Colors.ENDC}")
        name_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="cf-form-input2"]')))
        name_field.clear()
        name_field.send_keys(subdomain)
        time.sleep(random.uniform(1, 2))

        # Așteaptă apariția câmpului pentru IP și introdu IP-ul
        print(f"{Colors.OKCYAN}  🌐 Introducere IP: 34.202.63.170{Colors.ENDC}")
        ip_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'content')))
        ip_field.clear()
        ip_field.send_keys("34.202.63.170")
        time.sleep(random.uniform(1, 2))

        # Salvează înregistrarea
        print(f"{Colors.OKCYAN}  💾 Salvare înregistrare...{Colors.ENDC}")
        save_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
            '//*[@id="react-app"]/div/div/div/div[1]/div/div/main/div/div/div[2]/div[2]/div[2]/div[1]/form/div[5]/div/button[2]')))
        save_btn.click()

        # Așteaptă ca salvarea să fie efectuată
        time.sleep(random.uniform(2, 4))

        print(f"{Colors.OKGREEN}  ✓ Subdomeniu '{subdomain}' adăugat cu succes!{Colors.ENDC}")
        succes_count += 1

        # Progress bar
        print_progress_bar(index, total, subdomain)

    except Exception as e:
        print(f"{Colors.FAIL}  ✗ Eroare la procesarea '{subdomain}': {str(e)[:50]}...{Colors.ENDC}")
        error_count += 1

# Summary
print(f"\n\n{Colors.OKCYAN}{'═' * 70}{Colors.ENDC}")
print(f"{Colors.BOLD}📊 REZUMAT FINAL:{Colors.ENDC}")
print(f"{Colors.OKCYAN}{'═' * 70}{Colors.ENDC}")
print(f"  {Colors.OKGREEN}✓ Procesate cu succes: {succes_count}/{total}{Colors.ENDC}")
if error_count > 0:
    print(f"  {Colors.FAIL}✗ Erori: {error_count}/{total}{Colors.ENDC}")
print(f"{Colors.OKCYAN}{'═' * 70}{Colors.ENDC}\n")

print(f"{Colors.WARNING}⚠️  Browserul va rămâne deschis. Închide-l manual când ai terminat.{Colors.ENDC}")
# Închide browserul
# driver.quit()  # Comentează această linie dacă nu dorești să închizi browserul
