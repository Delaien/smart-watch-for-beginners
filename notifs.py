from init import *
from var import *

# liste des notifications
Notifs = []

# formate la notification pour l'afficher sur l'écran OLED
def format_notif(notif):
    formated = []

    for i in range(3):
        line = ""
        if len(notif) >= 16 and i == 2:
            line = notif[:13] + "..."
        elif len(notif) >= 16 and i != 2:
            line = notif[:16]
            notif = notif[16:]
        else:
            line = notif
            i = 4
        
        line = line.replace(u'\xa0', u' ')
        formated.append(str(line, 'utf-8'))

    return formated

# Interruption pour la réception de données par UART
def rcp_rx():
    global Notifs
    Notifs.append(format_notif(uart.read().decode().strip()))
    b_led.on()

uart.irq(rcp_rx)
        

# Affiche les notifications
def notifs():
    global Notifs, Status
    b_led.off()
    
    # Variables pour la navigation dans les notifications
    swap = 0
    swap_val = 0
    push = 0
    index = len(Notifs) - 1

    # Boucle principale
    while True:
        nb_notifs = len(Notifs)

        # Supprime la notification sélectionnée
        push = (getBMid(), push)[push != 0]
        if push != 0 and getBMid() == 0:
            if len(Notifs) > 0:
                del Notifs[index]
                index -= 1
                if len(Notifs) > 0:
                    index %= len(Notifs)
                else:
                    index = 0
            push = 0
            continue

        # Retour à l'écran précédent
        swap = (getBDown(), swap)[swap != 0]
        if swap != 0 and getBDown() == 0:
            return swap

        oled.fill(0)

        # Affiche le nombre de notifications et leur contenu
        if nb_notifs == 0:
            oled.fill_rect(39, 27, 10, 10, 1)
            oled.fill_rect(59, 27, 10, 10, 1)
            oled.fill_rect(79, 27, 10, 10, 1)
        else:
            for y, row in enumerate(NOTIFS):
                for x, c in enumerate(row):
                    oled.pixel(x, y, c)
            oled.text("%d" % nb_notifs, 14, 1)

            # Navigue vers les notifications précédentes
            swap_val = (getBUp(), swap_val)[swap_val != 0]
            if swap_val != 0 and getBUp() == 0:
                index -= swap_val
                index %= nb_notif
                swap_val = 0

        # Affiche la notification sélectionnée
        for i in range(len(Notifs[index])):
            oled.text(Notifs[index][i], 0, 22 + i * 10, 1)

    oled.show()
        