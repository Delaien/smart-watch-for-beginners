Ceci est une carte MicroPython

Vous pouvez commencer tout de suite en écrivant votre code Python dans 'main.py'.

Pour un serial prompt :

Windows : vous devez aller dans le 'Gestionnaire de périphériques', cliquez avec le bouton droit sur le périphérique inconnu,
puis mettre à jour le logiciel de pilote en utilisant le fichier 'pybcdc.inf' trouvé sur ce lecteur.
Ensuite, utilisez un programme de terminal comme Hyperterminal ou putty (dans notre cas nous avons utilisé putty pour les tests).
Mac OS X : utilisez la commande : screen /dev/tty.usbmodem*
Linux : utilisez la commande : screen /dev/ttyACM0

Si vous avez besoin de plus d'aide, merci de vous référer a ce site: http://micropython.org/help/.

Petit tour des Pins utilisés :
  - A5 : Bouton du haut
  - A6 : Bouton central
  - A7 : Bouton du bas
  - A0 : valeure du capteur SpO2
