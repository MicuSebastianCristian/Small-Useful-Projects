import time
import os

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
    BG_BLUE = '\033[44m'
    BG_GREEN = '\033[42m'

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print a beautiful banner for the application"""
    banner = f"""
{Colors.OKGREEN}{'╔' + '═' * 58 + '╗'}
║{Colors.BOLD}           💰 CALCULATOR BUGET ȘI SFATURI FINANCIARE 💰{Colors.ENDC}{Colors.OKGREEN}           ║
{'╚' + '═' * 58 + '╝'}{Colors.ENDC}
"""
    print(banner)

class CalculatorBuget:
    def __init__(self):
        self.venituri = 0
        self.cheltuieli = 0
        self.sold = 0
        self.istoric_venituri = []
        self.istoric_cheltuieli = []

    def adauga_venit(self, suma):
        self.venituri += suma
        self.sold += suma
        self.istoric_venituri.append(suma)

    def adauga_cheltuiala(self, suma):
        self.cheltuieli += suma
        self.sold -= suma
        self.istoric_cheltuieli.append(suma)

    def afiseaza_sold(self):
        print(f"\n{Colors.OKCYAN}{'─' * 60}{Colors.ENDC}")
        print(f"{Colors.BOLD}📊 INFORMAȚII FINANCIARE:{Colors.ENDC}")
        print(f"{Colors.OKCYAN}{'─' * 60}{Colors.ENDC}")
        print(f"  {Colors.OKGREEN}💵 Venituri totale:    {self.venituri:.2f} RON{Colors.ENDC}")
        print(f"  {Colors.FAIL}💸 Cheltuieli totale:  {self.cheltuieli:.2f} RON{Colors.ENDC}")

        if self.sold >= 0:
            print(f"  {Colors.OKGREEN}{Colors.BOLD}💰 Sold curent:        {self.sold:.2f} RON{Colors.ENDC}")
        else:
            print(f"  {Colors.FAIL}{Colors.BOLD}💰 Sold curent:        {self.sold:.2f} RON{Colors.ENDC}")

        print(f"{Colors.OKCYAN}{'─' * 60}{Colors.ENDC}\n")

    def sfaturi_economisire(self):
        print(f"\n{Colors.WARNING}{'─' * 60}{Colors.ENDC}")
        print(f"{Colors.BOLD}💡 SFATURI DE ECONOMISIRE:{Colors.ENDC}")
        print(f"{Colors.WARNING}{'─' * 60}{Colors.ENDC}")

        if self.venituri > self.cheltuieli:
            economisire_recomandata = (self.venituri - self.cheltuieli) * 0.2
            print(f"{Colors.OKGREEN}✓ Situație financiară bună!{Colors.ENDC}")
            print(f"\n{Colors.OKCYAN}📈 Recomandare:{Colors.ENDC}")
            print(f"  Economisiți cel puțin {Colors.BOLD}20%{Colors.ENDC} din surplus")
            print(f"  Suma recomandată: {Colors.BOLD}{Colors.OKGREEN}{economisire_recomandata:.2f} RON{Colors.ENDC}")

            # Additional tips
            print(f"\n{Colors.HEADER}💎 Sfaturi suplimentare:{Colors.ENDC}")
            print(f"  • Creați un fond de urgență de 3-6 luni din cheltuieli")
            print(f"  • Investiți în educație financiară")
            print(f"  • Diversificați sursele de venit")
        else:
            deficit = self.cheltuieli - self.venituri
            print(f"{Colors.FAIL}⚠ Atenție! Cheltuielile depășesc veniturile!{Colors.ENDC}")
            print(f"  Deficit: {Colors.FAIL}{Colors.BOLD}{deficit:.2f} RON{Colors.ENDC}")
            print(f"\n{Colors.WARNING}📉 Recomandări urgente:{Colors.ENDC}")
            print(f"  • Analizați și reduceți cheltuielile nenecesare")
            print(f"  • Creați un buget detaliat lunar")
            print(f"  • Căutați oportunități de venit suplimentar")
            print(f"  • Evitați creditele și datoriile noi")

        print(f"{Colors.WARNING}{'─' * 60}{Colors.ENDC}\n")

def print_menu():
    """Print the main menu with colors"""
    print(f"{Colors.OKCYAN}{'─' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}📋 MENIU PRINCIPAL:{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'─' * 60}{Colors.ENDC}")
    print(f"  {Colors.OKGREEN}1.{Colors.ENDC} 💵 Adaugă venit")
    print(f"  {Colors.FAIL}2.{Colors.ENDC} 💸 Adaugă cheltuială")
    print(f"  {Colors.OKBLUE}3.{Colors.ENDC} 📊 Afișează sold")
    print(f"  {Colors.WARNING}4.{Colors.ENDC} 💡 Sfaturi de economisire")
    print(f"  {Colors.HEADER}5.{Colors.ENDC} 🚪 Ieși din aplicație")
    print(f"{Colors.OKCYAN}{'─' * 60}{Colors.ENDC}")

calculator = CalculatorBuget()

clear_screen()
print_banner()

while True:
    print_menu()
    optiune = input(f"\n{Colors.BOLD}➜ Alege o opțiune (1-5): {Colors.ENDC}")

    if optiune == "1":
        try:
            suma_venit = float(input(f"{Colors.OKGREEN}💵 Introduceți suma venitului (RON): {Colors.ENDC}"))
            if suma_venit > 0:
                calculator.adauga_venit(suma_venit)
                print(f"\n{Colors.OKGREEN}✓ Venit de {suma_venit:.2f} RON adăugat cu succes!{Colors.ENDC}")
            else:
                print(f"\n{Colors.FAIL}✗ Suma trebuie să fie pozitivă!{Colors.ENDC}")
        except ValueError:
            print(f"\n{Colors.FAIL}✗ Vă rugăm să introduceți un număr valid!{Colors.ENDC}")
        time.sleep(2)
        clear_screen()
        print_banner()

    elif optiune == "2":
        try:
            suma_cheltuiala = float(input(f"{Colors.FAIL}💸 Introduceți suma cheltuielii (RON): {Colors.ENDC}"))
            if suma_cheltuiala > 0:
                calculator.adauga_cheltuiala(suma_cheltuiala)
                print(f"\n{Colors.WARNING}✓ Cheltuială de {suma_cheltuiala:.2f} RON adăugată cu succes!{Colors.ENDC}")
            else:
                print(f"\n{Colors.FAIL}✗ Suma trebuie să fie pozitivă!{Colors.ENDC}")
        except ValueError:
            print(f"\n{Colors.FAIL}✗ Vă rugăm să introduceți un număr valid!{Colors.ENDC}")
        time.sleep(2)
        clear_screen()
        print_banner()

    elif optiune == "3":
        calculator.afiseaza_sold()
        input(f"{Colors.OKCYAN}Apăsați ENTER pentru a continua...{Colors.ENDC}")
        clear_screen()
        print_banner()

    elif optiune == "4":
        calculator.sfaturi_economisire()
        input(f"{Colors.OKCYAN}Apăsați ENTER pentru a continua...{Colors.ENDC}")
        clear_screen()
        print_banner()

    elif optiune == "5":
        print(f"\n{Colors.OKGREEN}{'═' * 60}{Colors.ENDC}")
        print(f"{Colors.BOLD}👋 Vă mulțumim pentru utilizarea aplicației!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{'═' * 60}{Colors.ENDC}\n")
        break
    else:
        print(f"\n{Colors.FAIL}✗ Opțiune invalidă! Vă rugăm să alegeți o opțiune între 1-5.{Colors.ENDC}")
        time.sleep(2)
        clear_screen()
        print_banner()
