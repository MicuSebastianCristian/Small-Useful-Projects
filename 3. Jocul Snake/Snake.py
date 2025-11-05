import pygame
from random import randint

pygame.init()

# Enhanced Color Palette - Modern and vibrant
ALB = (255, 255, 255)
NEGRU = (20, 20, 30)  # Darker black for better contrast
GRI_INCHIS = (40, 40, 50)
GRI_DESCHIS = (60, 60, 70)

# Snake colors - Gradient green
VERDE_CAP = (50, 255, 100)  # Bright green for head
VERDE_CORP = (30, 200, 80)  # Darker green for body

# Food colors - Vibrant red/pink
ROSU_MANCARE = (255, 50, 80)
ROZ = (255, 100, 130)

# UI Colors
ALBASTRU_UI = (100, 150, 255)
GALBEN_SCOR = (255, 220, 50)

LATIME, INALTIME = 600, 650  # Extra space for score display

DIMENSIUNE_CELULA = 15
SARPE = [(5, 5), (5, 4), (5, 3)]
MANCARE = (10, 10)
DIRECTION = 'DREAPTA'
ESTE_SFARSIT_JOC = False
SCOR = 0

ecran = pygame.display.set_mode((LATIME, INALTIME))
pygame.display.set_caption('🐍 Jocul Șarpelui - Modern Edition')

# Fonts
font_mic = pygame.font.Font(None, 24)
font_mediu = pygame.font.Font(None, 36)
font_mare = pygame.font.Font(None, 48)


def deseneaza_sarpe():
    """Draw snake with gradient effect - head is brighter"""
    for i, segment in enumerate(SARPE):
        x = segment[0] * DIMENSIUNE_CELULA
        y = segment[1] * DIMENSIUNE_CELULA

        if i == 0:  # Head
            # Draw head with border
            pygame.draw.rect(ecran, VERDE_CAP, (x + 1, y + 1, DIMENSIUNE_CELULA - 2, DIMENSIUNE_CELULA - 2), border_radius=3)
            pygame.draw.rect(ecran, ALB, (x + 1, y + 1, DIMENSIUNE_CELULA - 2, DIMENSIUNE_CELULA - 2), 1, border_radius=3)
        else:  # Body
            pygame.draw.rect(ecran, VERDE_CORP, (x + 1, y + 1, DIMENSIUNE_CELULA - 2, DIMENSIUNE_CELULA - 2), border_radius=2)


def deseneaza_mancare():
    """Draw food with pulsating effect"""
    x = MANCARE[0] * DIMENSIUNE_CELULA
    y = MANCARE[1] * DIMENSIUNE_CELULA

    # Draw outer glow
    pygame.draw.rect(ecran, ROZ, (x, y, DIMENSIUNE_CELULA, DIMENSIUNE_CELULA), border_radius=4)
    # Draw inner bright center
    pygame.draw.rect(ecran, ROSU_MANCARE, (x + 2, y + 2, DIMENSIUNE_CELULA - 4, DIMENSIUNE_CELULA - 4), border_radius=3)


def deseneaza_grid():
    """Draw subtle grid lines"""
    for x in range(0, LATIME, DIMENSIUNE_CELULA):
        pygame.draw.line(ecran, GRI_INCHIS, (x, 50), (x, 600), 1)
    for y in range(50, 600, DIMENSIUNE_CELULA):
        pygame.draw.line(ecran, GRI_INCHIS, (0, y), (LATIME, y), 1)


def deseneaza_scor():
    """Draw score and game info at the top"""
    # Draw top bar background
    pygame.draw.rect(ecran, GRI_INCHIS, (0, 0, LATIME, 50))
    pygame.draw.line(ecran, ALBASTRU_UI, (0, 50), (LATIME, 50), 2)

    # Score text
    scor_text = font_mediu.render(f'Scor: {SCOR}', True, GALBEN_SCOR)
    ecran.blit(scor_text, (20, 10))

    # Length text
    lungime_text = font_mic.render(f'Lungime: {len(SARPE)}', True, ALB)
    ecran.blit(lungime_text, (250, 15))

    # Controls hint
    control_text = font_mic.render('Săgeți pentru control', True, GRI_DESCHIS)
    ecran.blit(control_text, (420, 15))


def aparitie_mancare():
    """Generate new food position avoiding snake body"""
    while True:
        x = randint(0, (LATIME // DIMENSIUNE_CELULA) - 1)
        y = randint(3, (600 // DIMENSIUNE_CELULA) - 1)  # Avoid top bar
        if (x, y) not in SARPE:
            return (x, y)


ceas = pygame.time.Clock()
scor_maxim = 0

while True:
    ESTE_SFARSIT_JOC = False
    SARPE = [(5, 5), (5, 4), (5, 3)]
    MANCARE = (10, 10)
    DIRECTION = 'DREAPTA'
    SCOR = 0

    while not ESTE_SFARSIT_JOC:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ESTE_SFARSIT_JOC = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and DIRECTION != 'DREAPTA':
                    DIRECTION = 'STANGA'
                elif event.key == pygame.K_RIGHT and DIRECTION != 'STANGA':
                    DIRECTION = 'DREAPTA'
                elif event.key == pygame.K_UP and DIRECTION != 'JOS':
                    DIRECTION = 'SUS'
                elif event.key == pygame.K_DOWN and DIRECTION != 'SUS':
                    DIRECTION = 'JOS'

        cap = SARPE[0]
        if DIRECTION == 'STANGA':
            noua_cap = ((cap[0] - 1) % (LATIME // DIMENSIUNE_CELULA), cap[1])
        elif DIRECTION == 'DREAPTA':
            noua_cap = ((cap[0] + 1) % (LATIME // DIMENSIUNE_CELULA), cap[1])
        elif DIRECTION == 'SUS':
            noua_cap = (cap[0], (cap[1] - 1) % (600 // DIMENSIUNE_CELULA))
        elif DIRECTION == 'JOS':
            noua_cap = (cap[0], (cap[1] + 1) % (600 // DIMENSIUNE_CELULA))

        SARPE = [noua_cap] + SARPE[:-1]

        if noua_cap in SARPE[1:]:
            ESTE_SFARSIT_JOC = True

        if noua_cap == MANCARE:
            SARPE.append(SARPE[-1])
            MANCARE = aparitie_mancare()
            SCOR += 10  # Increase score
            if SCOR > scor_maxim:
                scor_maxim = SCOR

        ecran.fill(NEGRU)
        deseneaza_grid()
        deseneaza_sarpe()
        deseneaza_mancare()
        deseneaza_scor()
        pygame.display.flip()

        ceas.tick(10)

    # Modern Game Over Screen
    # Semi-transparent overlay
    overlay = pygame.Surface((LATIME, INALTIME))
    overlay.set_alpha(200)
    overlay.fill(NEGRU)
    ecran.blit(overlay, (0, 0))

    # Game Over box
    box_width, box_height = 500, 350
    box_x = (LATIME - box_width) // 2
    box_y = (INALTIME - box_height) // 2

    # Draw box with border
    pygame.draw.rect(ecran, GRI_INCHIS, (box_x, box_y, box_width, box_height), border_radius=15)
    pygame.draw.rect(ecran, ALBASTRU_UI, (box_x, box_y, box_width, box_height), 3, border_radius=15)

    # Title
    text_game_over = font_mare.render("GAME OVER", True, ROSU_MANCARE)
    ecran.blit(text_game_over, (box_x + (box_width - text_game_over.get_width()) // 2, box_y + 30))

    # Score display
    text_scor_final = font_mediu.render(f"Scor Final: {SCOR}", True, GALBEN_SCOR)
    ecran.blit(text_scor_final, (box_x + (box_width - text_scor_final.get_width()) // 2, box_y + 100))

    # High score
    text_scor_maxim = font_mic.render(f"Scor Maxim: {scor_maxim}", True, ALBASTRU_UI)
    ecran.blit(text_scor_maxim, (box_x + (box_width - text_scor_maxim.get_width()) // 2, box_y + 140))

    # Length
    text_lungime = font_mic.render(f"Lungime Finală: {len(SARPE)}", True, ALB)
    ecran.blit(text_lungime, (box_x + (box_width - text_lungime.get_width()) // 2, box_y + 180))

    # Instructions
    text_nou = font_mediu.render("Apasă ENTER pentru joc nou", True, VERDE_CAP)
    ecran.blit(text_nou, (box_x + (box_width - text_nou.get_width()) // 2, box_y + 230))

    # Author
    text_autor = font_mic.render("Joc realizat de Micu Sebastian Cristian", True, GRI_DESCHIS)
    ecran.blit(text_autor, (box_x + (box_width - text_autor.get_width()) // 2, box_y + 290))

    pygame.display.flip()

    asteptare_input = True
    while asteptare_input:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                asteptare_input = False
    pygame.event.clear()

pygame.quit()
