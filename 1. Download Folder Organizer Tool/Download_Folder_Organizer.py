import os
import shutil


# Funcția care mă ajută să organizez fișierele din folderul "Downloads"
def organize_folder_descarcari():
    # Obțin calea către folderul "Downloads" al meu
    cale_descarcari = os.path.expanduser('~') + '/Downloads'

    # Verific dacă folderul "Downloads" există pentru mine
    if not os.path.exists(cale_descarcari):
        print("Folderul 'Downloads' meu nu există!")
        return

    # Trec prin fiecare fișier din folderul "Downloads"
    for nume_fisier in os.listdir(cale_descarcari):
        # Verific dacă fișierul este cu adevărat un fișier și nu un director
        if os.path.isfile(os.path.join(cale_descarcari, nume_fisier)) and nume_fisier != "Main.py":
            # Obțin extensia fișierului meu
            extensie_fisier = nume_fisier.split('.')[-1]
            # Creez sau obțin calea către folderul meu de destinație, corespunzător extensiei
            folder_destinatie = os.path.join(cale_descarcari, extensie_fisier.upper())

            # Verific dacă folderul de destinație există și, dacă nu, îl creez
            if not os.path.exists(folder_destinatie):
                os.mkdir(folder_destinatie)

            # Obțin căile către fișierul meu sursă și fișierul meu destinație
            cale_sursa = os.path.join(cale_descarcari, nume_fisier)
            cale_destinatie = os.path.join(folder_destinatie, nume_fisier)

            try:
                # Mut fișierul meu în folderul de destinație
                shutil.move(cale_sursa, cale_destinatie)
                print(f"Am mutat '{nume_fisier}' în '{folder_destinatie}'")
            except (shutil.Error, PermissionError) as e:
                # În caz că apar erori la mutare, afișez un mesaj și continui cu următorul meu fișier
                print(f"Eroare la mutarea '{nume_fisier}': {e}. Trec peste.")


# Punctul de intrare în program, adică aici începe totul pentru mine
if __name__ == "__main__":
    organize_folder_descarcari()
