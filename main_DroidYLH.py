#import time
#import string
#import random
#import json
#from selenium.webdriver.common.by import By
#import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from droidTwitterActions import *



# TODO
# Refatorar e abstrair mais o código
# OOP

# You Like Hits e Twitter Variáveis
ylh_sign_in = 'https://www.youlikehits.com/login.php'
twitter_sign_in = 'https://www.twitter.com/i/flow/login'
ylh_twitter_follow = 'https://www.youlikehits.com/twitter2.php'
ylh_twitter_like = 'https://www.youlikehits.com/favtweets.php'
bonus_points = 'https://www.youlikehits.com/bonuspoints.php'

# Abrir configurações de login
settings = importSettings()

# Definir o Chromedriver
caps = DesiredCapabilities().CHROME
caps['pageLoadStrategy'] = 'normal'
chromeOptions = Options()
if settings['headlessmode']:
	chromeOptions.add_argument('--headless')
chromeOptions.add_argument('--mute-audio')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chromeOptions, desired_capabilities=caps)

########   Wait para checar a presença do elemento nas funções   ########
wait = WebDriverWait(driver, 20)

########   Login twitter   ########
twitterLogin(driver, settings, twitter_sign_in, wait)

########   Login You Like Hits   ########
youLikeHitsLogin(driver, settings, ylh_sign_in)

########   Confirmar com Enter   ########
if settings['headlessmode'] == False:  # not settings['headlessmode']
	input('Enter para confirmar Login')

########   Pegar a quantidade de pontos atuais   ########
startpoints = getStartPoints(driver)

########   Função dos LIKES   ########
twitterLikes(driver, ylh_twitter_like, wait)

########   Função para seguir no Twitter   ########
twitterFollow(driver, ylh_twitter_follow, wait)

########   Mostrar total de pontos ganhos   ########
showEarnedPoints(driver, startpoints)

# TODO
# Contar os hits do dia e pegar o bônus
#bonusPoints(driver, bonus_points)

# TODO
# Implementar captura de KeyboardInterrupt
# Para finalizar o programa

#TODO apagar caso seja pra finalizar com ctrl + c
input("Enter para finalizar!")
########   Fechar o navegador   ########
driver.quit()
