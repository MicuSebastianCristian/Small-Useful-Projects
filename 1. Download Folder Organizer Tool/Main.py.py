import os
import shutil

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
{Colors.OKCYAN}{'═' * 60}
{Colors.BOLD}    📁 ORGANIZATOR FOLDER DESCĂRCĂRI 📁{Colors.ENDC}
{Colors.OKCYAN}{'═' * 60}{Colors.ENDC}
"""
    print(banner)

def organize_folder_descarcari():
    mapare_tipuri = {
        "Audio": {"extensions": ["mp3", "wav", "flac", "aac", "ogg"], "icon": "🎵"},
        "Video": {"extensions": ["mp4", "avi", "mkv", "flv", "wmv"], "icon": "🎬"},
        "Documente": {"extensions": ["doc", "docx", "pdf", "txt", "xlsx", "ppt", "pptx"], "icon": "📄"},
        "Imagini": {"extensions": ["jpg", "jpeg", "png", "gif", "bmp", "tiff"], "icon": "🖼️"},
        "Executabile": {"extensions": ["exe", "msi", "bat", "sh"], "icon": "⚙️"},
        "Arhive": {"extensions": ["zip", "rar", "tar", "7z"], "icon": "📦"},
    }

    print_banner()
    cale_descarcari = os.path.expanduser('~') + '/Downloads'

    if not os.path.exists(cale_descarcari):
        print(f"{Colors.FAIL}✗ Folderul 'Downloads' nu există!{Colors.ENDC}")
        return

    print(f"{Colors.OKBLUE}📍 Cale: {cale_descarcari}{Colors.ENDC}\n")

    fisiere_mutate = 0
    fisiere_eroare = 0

    for nume_fisier in os.listdir(cale_descarcari):
        if os.path.isfile(os.path.join(cale_descarcari, nume_fisier)) and nume_fisier != "Main.py":
            extensie_fisier = nume_fisier.split('.')[-1].lower()

            folder_destinatie = "Altele"
            icon = "📋"

            for tip, info in mapare_tipuri.items():
                if extensie_fisier in info["extensions"]:
                    folder_destinatie = tip
                    icon = info["icon"]
                    break

            folder_destinatie_path = os.path.join(cale_descarcari, folder_destinatie)
            if not os.path.exists(folder_destinatie_path):
                os.mkdir(folder_destinatie_path)
                print(f"{Colors.OKCYAN}📁 Folder nou creat: {folder_destinatie}{Colors.ENDC}")

            cale_sursa = os.path.join(cale_descarcari, nume_fisier)
            cale_destinatie = os.path.join(folder_destinatie_path, nume_fisier)

            try:
                shutil.move(cale_sursa, cale_destinatie)
                print(f"{Colors.OKGREEN}✓ {icon} {nume_fisier}{Colors.ENDC} → {Colors.BOLD}{folder_destinatie}{Colors.ENDC}")
                fisiere_mutate += 1
            except (shutil.Error, PermissionError) as e:
                print(f"{Colors.FAIL}✗ Eroare: '{nume_fisier}': {e}{Colors.ENDC}")
                fisiere_eroare += 1

    # Print summary
    print(f"\n{Colors.OKCYAN}{'═' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}📊 REZUMAT:{Colors.ENDC}")
    print(f"  {Colors.OKGREEN}✓ Fișiere mutate: {fisiere_mutate}{Colors.ENDC}")
    if fisiere_eroare > 0:
        print(f"  {Colors.FAIL}✗ Erori: {fisiere_eroare}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'═' * 60}{Colors.ENDC}")

# Code written by Micu Sebastian

if __name__ == "__main__":
    organize_folder_descarcari()
