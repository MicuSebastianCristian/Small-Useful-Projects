import pygame
from random import randint

pygame.init()

ALB = (255, 255, 255)
VERDE = (0, 255, 0)
ROSU = (255, 0, 0)
NEGRU = (0, 0, 0)

LATIME, INALTIME = 600, 600

DIMENSIUNE_CELULA = 15
SARPE = [(5, 5), (5, 4), (5, 3)]
MANCARE = (10, 10)
DIRECTION = 'DREAPTA'
ESTE_SFARSIT_JOC = False

ecran = pygame.display.set_mode((LATIME, INALTIME))
pygame.display.set_caption('Jocul Sarpelui')


def deseneaza_sarpe():
    for segment in SARPE:
        pygame.draw.rect(ecran, VERDE, (
        segment[0] * DIMENSIUNE_CELULA, segment[1] * DIMENSIUNE_CELULA, DIMENSIUNE_CELULA, DIMENSIUNE_CELULA))


def deseneaza_mancare():
    pygame.draw.rect(ecran, ROSU, (
    MANCARE[0] * DIMENSIUNE_CELULA, MANCARE[1] * DIMENSIUNE_CELULA, DIMENSIUNE_CELULA, DIMENSIUNE_CELULA))


def aparitie_mancare():
    while True:
        x = randint(0, (LATIME // DIMENSIUNE_CELULA) - 1)
        y = randint(0, (INALTIME // DIMENSIUNE_CELULA) - 1)
        if (x, y) not in SARPE:
            return (x, y)


ceas = pygame.time.Clock()
while True:
    ESTE_SFARSIT_JOC = False
    SARPE = [(5, 5), (5, 4), (5, 3)]
    MANCARE = (10, 10)
    DIRECTION = 'DREAPTA'

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
            noua_cap = (cap[0], (cap[1] - 1) % (INALTIME // DIMENSIUNE_CELULA))
        elif DIRECTION == 'JOS':
            noua_cap = (cap[0], (cap[1] + 1) % (INALTIME // DIMENSIUNE_CELULA))

        SARPE = [noua_cap] + SARPE[:-1]

        if noua_cap in SARPE[1:]:
            ESTE_SFARSIT_JOC = True

        if noua_cap == MANCARE:
            SARPE.append(SARPE[-1])
            MANCARE = aparitie_mancare()

        ecran.fill(NEGRU)
        deseneaza_sarpe()
        deseneaza_mancare()
        pygame.display.flip()

        ceas.tick(10)

    font = pygame.font.Font(None, 36)
    text_sfarsit_joc = font.render("Sfârșitul jocului", True, ALB)
    text_autor = font.render("Joc realizat de Micu Sebastian Cristian", True, ALB)
    text_nou = font.render("Apasă ENTER pentru un joc nou", True, ALB)  # Text nou
    ecran.blit(text_sfarsit_joc, (LATIME // 2 - text_sfarsit_joc.get_width() // 2, INALTIME // 2 - 18))
    ecran.blit(text_autor, (LATIME // 2 - text_autor.get_width() // 2, INALTIME // 2 + 18))
    ecran.blit(text_nou, (LATIME // 2 - text_nou.get_width() // 2, INALTIME // 2 + 54))  # Ajustare coordonată y
    pygame.display.flip()

    asteptare_input = True
    while asteptare_input:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                asteptare_input = False
    pygame.event.clear()

pygame.quit()
