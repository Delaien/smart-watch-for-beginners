from init import *
from var import *

def printTime(now, last):
    """
    Affiche l'heure et la date sur l'écran OLED
    now : temps actuel (struct_time)
    last : dernier temps affiché (struct_time)
    """
    oled.fill(0)  # Effacement de l'écran OLED
    h = ("", "0")[now[3] < 10] + str(now[3])  # Formatage de l'heure (ajout d'un 0 si < 10)
    sep = (":", " ")[last[5] != now[5]]  # Séparateur entre heure et minute (: si seconde a changé, sinon espace)
    m = ("", "0")[now[4] < 10] + str(now[4])  # Formatage des minutes (ajout d'un 0 si < 10)
    s = ("", "0")[now[5] < 10] + str(now[5])  # Formatage des secondes (ajout d'un 0 si < 10)
    date = DAY[now[6]] + " " + str(now[2]) + " " + MONTH[now[1]] + " " + str(now[0])  # Formatage de la date

    write(5, 5, h, CC, 48, 32, 1, 4)  # Affichage de l'heure
    write(53, 5, sep, CC, 9, 32, 1, 3)  # Affichage du séparateur
    write(62, 5, m, CC, 48, 32, 1, 4)  # Affichage des minutes
    write(110, 5, s, CC, 13, 32, 1, 1)  # Affichage des secondes
    write(0, 37, date, CC, 128, 32, 1, 1)  # Affichage de la date

def fh(val):
    """
    Fonction de formatage de l'heure pour éviter les valeurs incorrectes
    val : heure (int)
    """
    if val < 0:
        return 23
    elif val >= 24:
        return 0
    return val

def fms(val):
    """
    Fonction de formatage des minutes et des secondes pour éviter les valeurs incorrectes
    val : minutes/secondes (int)
    """
    if val < 0:
        return 59
    elif val >= 60:
        return 0
    return val

def fd(val):
    """
    Fonction de formatage du jour de la semaine pour éviter les valeurs incorrectes
    val : jour de la semaine (int)
    """
    if val < 0:
        return 6
    elif val >= 7:
        return 0
    return val

def fdn(val):
    """
    Fonction de formatage du jour du mois pour éviter les valeurs incorrectes
    val : jour du mois (int)
    """
    if val < 1:
        return 31
    elif val >= 32:
        return 1
    return val

def fm(val):
    """
    Fonction de formatage du mois pour éviter les valeurs incorrectes
    val : mois (int)
    """
    if val < 1:
        return 12
    elif val >= 13:
        return 1
    return val

def fy(val):
    """
    Fonction de formatage de l'année pour éviter les valeurs incorrectes
    val : année (int)
    """
    if val < 0:
        return 0
    return val

def settime():
    """
    Fonction permettant de régler l'heure
    """
    now = utime.gmtime()  # Récupération de l'heure actuelle
    printTime(now, now)  # Affichage de l'heure actuelle
    oled.show()  # Mise à jour de l'écran OLED

    val = [now[3], now[4], now[5], now[6], now[2], now[1], now[0]]  # Stockage des valeurs de l'heure dans un tableau
    format_val = [fh, fms, fms, fd, fdn, fm, fy]  # Tableau des fonctions de formatage pour chaque valeur de l'heure
    index = 0  # Index de la valeur de l'heure à régler

    swap_val = 0  # Variable pour stocker l'action de scroll
    swap = 0  # Variable pour stocker la direction du scroll

    while index < 7:  # Boucle jusqu'à ce que toutes les valeurs de l'heure soient réglées
        swap_val = (getBMid(), swap_val)[swap_val != 0]  # Récupération de l'action de scroll (bouton pressé/relâché)
        if swap_val != 0 and getBMid() == 0:  # Si le bouton a été relâché
            index += 1  # Passage à la valeur suivante de l'heure
            swap_val = 0  # Remise à zéro de la variable d'action de scroll

        swap = (getVrY(), swap)[swap != 0]  # Récupération de la direction du scroll (haut/bas)
        if swap != 0 and getVrY() == 0:  # Si le scroll a été relâché
            val[index] = format_val[index](val[index] + swap)  # Modification de la valeur de l'heure en utilisant la fonction de formatage correspondante
            swap = 0  # Remise à zéro de la variable de direction de scroll

        new = (val[6], val[5], val[4], val[0], val[1], val[2], val[3], 0)  # Mise à jour de la variable de temps avec les nouvelles valeurs
        machine.RTC().datetime((new[0], new[1], new[2], new[6] + 1, new[3], new[4], new[5], 0))  # Enregistrement de la nouvelle date et heure dans le module RTC
        printTime(new, new)  # Affichage de la nouvelle date et heure
        oled.show()  # Mise à jour de l'écran OLED

def watch():    
    """
    Fonction principale pour afficher l'heure et gérer les entrées utilisateur
    """
    last = utime.gmtime()  # Récupération de l'heure actuelle pour la dernière mise à jour de l'affichage
    swap = 0  # Variable pour stocker la direction du scroll
    push = 0  # Variable pour stocker l'action de pression sur le bouton

    while True:  # Boucle infinie pour l'affichage de l'heure en temps réel
        swap = (getVrY(), swap)[swap != 0]  # Récupération de la direction du scroll (haut/bas)
        if swap != 0 and getVrY() == 0:  # Si le scroll a été relâché
            return swap  # Retourne la direction du scroll (utile pour d'autres fonctionnalités)

        push = (getBMid(), push)[push != 0]  # Récupération de l'action de pression sur le bouton (pressé/relâché)
        if push != 0 and getBMid() == 0:  # Si le bouton a été relâché
            settime()  # Lance la fonction de réglage de l'heure
            push = 0  # Remise à zéro de la variable d'action de pression sur le bouton

        now = utime.gmtime()  # Récupération de l'heure actuelle
        printTime(now, last)  # Affichage de l'heure actuelle

        oled.show()  # Mise à jour de l'écran OLED
        last = now  # Mise à jour de la dernière heure affichée