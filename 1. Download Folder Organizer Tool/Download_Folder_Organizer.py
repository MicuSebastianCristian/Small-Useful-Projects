import os
import shutil

def organize_folder_descarcari():
    mapare_tipuri = {
        "Audio": ["mp3", "wav", "flac", "aac", "ogg"],
        "Video": ["mp4", "avi", "mkv", "flv", "wmv"],
        "Documente": ["doc", "docx", "pdf", "txt", "xlsx", "ppt", "pptx"],
        "Imagini": ["jpg", "jpeg", "png", "gif", "bmp", "tiff"],
        "Executabile": ["exe", "msi", "bat", "sh"],
        "Arhive": ["zip", "rar", "tar", "7z"],
    }

    cale_descarcari = os.path.expanduser('~') + '/Downloads'

    if not os.path.exists(cale_descarcari):
        print("Folderul 'Downloads' meu nu există!")
        return

    for nume_fisier in os.listdir(cale_descarcari):
        if os.path.isfile(os.path.join(cale_descarcari, nume_fisier)) and nume_fisier != "Main.py":
            extensie_fisier = nume_fisier.split('.')[-1].lower()

            folder_destinatie = "Altele"
            for tip, extensii in mapare_tipuri.items():
                if extensie_fisier in extensii:
                    folder_destinatie = tip
                    break

            folder_destinatie = os.path.join(cale_descarcari, folder_destinatie)
            if not os.path.exists(folder_destinatie):
                os.mkdir(folder_destinatie)

            cale_sursa = os.path.join(cale_descarcari, nume_fisier)
            cale_destinatie = os.path.join(folder_destinatie, nume_fisier)

            try:
                shutil.move(cale_sursa, cale_destinatie)
                print(f"Am mutat '{nume_fisier}' în '{folder_destinatie}'")
            except (shutil.Error, PermissionError) as e:
                print(f"Eroare la mutarea '{nume_fisier}': {e}. Trec peste.")

# Code written by Micu Sebastian

if __name__ == "__main__":
    organize_folder_descarcari()
