from init import *
from var import *
import random

# Seuil de montée pour la détection du rythme cardiaque
RISE_THRESHOLD = 4
# Nombre maximum de lectures pour la détection du rythme cardiaque
MAX_READS = 4

# Valeurs simulées de rythme cardiaque
beatval = [0, 1, 2, 1, 0, 0, -1, 10, -3, 0, 0, 0, 1, 2, 0, 1, 0]

# Fonction pour rafraîchir l'affichage OLED
def refresh(i):
    # Défilement de l'écran vers la gauche
    oled.scroll(-1, 0)
    oled.scroll(-1, 0)

    # Effacement de la zone de texte
    oled.fill_rect(0, 0, 128, 16, 0) 
    
    # Affichage de l'image d'un coeur lorsque i est entre 7 et 10
    if i >= 7 and i <= 10:
        for y, row in enumerate(HEART):
            for x, c in enumerate(row):
                oled.pixel(x, y, c)

    # Affichage du nombre de BPM
    oled.text("%d bpm" % 56, 14, 1)
    # Tracé d'une ligne représentant la valeur de rythme cardiaque actuelle
    oled.line(124, 48 - 2 * beatval[i - 1], 126, 48 - 2 * beatval[i], 1)

    oled.show()

def heartbeat():
    # Effacement de l'écran OLED
    oled.fill(0)
    oled.show()

    # Activation des composants spoVolt et sensorVolt
    spoVolt.value(1)
    sensorVolt.value(1)
    time.sleep(0.05)

    swap = 0
    i = 0
    y = 0

    # Boucle principale de la mesure de rythme cardiaque
    while True:
        # Lecture de la valeur de rythme cardiaque
        swap = (getVrY(), swap)[swap != 0]
        if swap != 0 and getVrY() == 0:
            spoVolt.value(0)
            sensorVolt.value(0)
            time.sleep(0.05)
            return swap
        # Mise à jour de l'affichage OLED
        refresh(i)
        i = (i + 1) % len(beatval)
        time.sleep(0.02)