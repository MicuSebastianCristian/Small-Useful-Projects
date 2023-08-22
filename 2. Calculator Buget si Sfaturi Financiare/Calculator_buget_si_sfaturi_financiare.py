import time

class CalculatorBuget:
    def __init__(self):
        self.venituri = 0
        self.cheltuieli = 0
        self.sold = 0

    def adauga_venit(self, suma):
        self.venituri += suma
        self.sold += suma

    def adauga_cheltuiala(self, suma):
        self.cheltuieli += suma
        self.sold -= suma

    def afiseaza_sold(self):
        print(f"Soldul curent este: {self.sold}")

    def sfaturi_economisire(self):
        if self.venituri > self.cheltuieli:
            economisire_recomandata = (self.venituri - self.cheltuieli) * 0.2
            print(f"Recomandarea pentru economisire: Economisiți cel puțin 20% din soldul total, adica {economisire_recomandata:.2f}")
        else:
            print("Recomandarea pentru economisire: Încercați să economisiți mai mult pentru a vă echilibra bugetul.")


calculator = CalculatorBuget()

while True:
    print("\n1. Adaugă venit")
    print("2. Adaugă cheltuială")
    print("3. Afisează sold")
    print("4. Sfaturi de economisire")
    print("5. Ieși din aplicație")

    optiune = input("Alege o opțiune: ")

    if optiune == "1":
        suma_venit = float(input("Introduceți suma venitului: "))
        calculator.adauga_venit(suma_venit)
        print("Venit adăugat cu succes!")
        time.sleep(3)
    elif optiune == "2":
        suma_cheltuiala = float(input("Introduceți suma cheltuielii: "))
        calculator.adauga_cheltuiala(suma_cheltuiala)
        print("Cheltuială adăugată cu succes!")
        time.sleep(3)
    elif optiune == "3":
        calculator.afiseaza_sold()
        time.sleep(3)
    elif optiune == "4":
        calculator.sfaturi_economisire()
        time.sleep(3)
    elif optiune == "5":
        print("Aplicația a fost închisă.")
        break
    else:
        print("Opțiune invalidă. Vă rugăm să introduceți o opțiune validă.")
        time.sleep(3)
