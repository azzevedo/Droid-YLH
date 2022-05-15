#!/usr/bin/python3
from automata import Marvin



marvin = Marvin()
marvin.setupDriver()
marvin.twitterLogin()
marvin.youLikeHitsLogin()
marvin.confirmLogin()
marvin.twitterLikes()
marvin.twitterFollow()
#TODO instagramLikes()
#TODO pinterestFollow()
marvin.showEarnedPoints()

# marvin.bonusPoints()

# TODO
# Implementar captura de KeyboardInterrupt
# Para finalizar o programa

#TODO apagar linha abaixo caso seja pra finalizar com ctrl + c
input("Enter para finalizar!")
########   Fechar o navegador   ########
marvin.goodbye()
