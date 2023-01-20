from init import *
from var import *
import random

#Fonction qui génère une pipe aléatoire
def generate_pipe():
    #Création d'une liste de 64 pixels allumés
    pipe = [1 for i in range(64)]

    #Sélection d'une position aléatoire pour le haut de la pipe
    top = random.randint(5, 40)
    #Eteindre les pixels pour créer le trou de la pipe
    for i in range(top, top + 20):
        pipe[i] = 0

    return pipe
    
def flappy():
    #Effacement de l'écran OLED
    oled.fill(0)
    oled.show()

    #Intervalle de temps entre chaque génération de pipe
    TIMING = 4000
    #Initialisation du compteur de temps
    clock = utime.ticks_ms() - TIMING 

    #Position initiale de l'oiseau
    bird_pos = [63, 31]
    #Score initial
    score = 0

    #Boucle principale du jeu
    while True:
        #Effacement de la précédente position de l'oiseau
        oled.pixel(bird_pos[0], bird_pos[1], 0)
        #Déplacement de l'écran vers la gauche
        oled.scroll(-1, 0)

        #Modification de la position verticale de l'oiseau en fonction de la valeur de getVrY()
        if getVrY() != 0:
            bird_pos[1] -= 5
        else:
            bird_pos[1] += 2

        #Vérification de collision
        if oled.pixel(bird_pos[0], bird_pos[1]) or bird_pos[1] < 0 or bird_pos[1] >= 64:
            break

        #Incrémente le score si l'oiseau passe une pipe
        score += int(oled.pixel(bird_pos[0] - 1, 0) and not oled.pixel(bird_pos[0], 0))
        
        #Dessine l'oiseau à sa nouvelle position
        oled.pixel(bird_pos[0], bird_pos[1], 1)

        #Vérifie si TIMING ms se sont écoulées depuis la dernière génération de pipe
        if utime.ticks_ms() - clock >= TIMING:
            pipe = generate_pipe()

            #Dessine la nouvelle pipe
            for i in range(len(pipe)):
                oled.pixel(124, i, pipe[i])
                oled.pixel(125, i, pipe[i])
                oled.pixel(126, i, pipe[i])
            
            #Réinitialise le compteur de temps
            clock = utime.ticks_ms()
        
        #Affiche les modifications sur l'écran OLED
        oled.show()

