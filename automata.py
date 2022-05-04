#!/usr/bin/python3
import os
import json
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException



class Marvin():
	"""
	Automação de ações no site youlikehits.com
	Likes e Follow no twitter
	"""

	def __init__(self):
		self.__settings = self.__importSettings()
		self.driver = None
		self._wait = None
		self.startpoints = None


	def setupDriver(self):
		# Definir configurações do driver
		caps = DesiredCapabilities().CHROME
		caps['pageLoadStrategy'] = 'normal'
		chromeOptions = Options()
		if self.__settings['headlessmode']:
			chromeOptions.add_argument('--headless')
		chromeOptions.add_argument('--mute-audio')
		# Melhor instanciar o driver aqui pra não abrir o navegador toda vez que importar a classe em outro arquivo
		self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chromeOptions, desired_capabilities=caps)
		self._wait = WebDriverWait(self.driver, 20)


	def __importSettings(self):
		# Abrir configurações do arquivo json
		settingU = json.load(open('twitter.json'))
		jcopy = json.dumps(settingU)
		setting = json.loads(jcopy)
		return setting


	def twitterLogin(self):
		# Login no twitter
		url = 'https://www.twitter.com/i/flow/login'
		self.driver.get(url)
		time.sleep(7)

		### Elemento de Username
		el = self._wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[5]/label/div/div[2]/div/input')))
		el.send_keys(self.__settings['twitterUsername'])
		self.delay()

		# Botão avançar
		el = self._wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[6]/div')))
		el.click()
		self.delay()

		### Elemento de Senha
		el = self._wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')))
		el.send_keys(self.__settings['twitterPassword'])
		self.delay()
		
		# Login com senha inserida
		el = self.el = self._wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div')))
		el.click()
		self.delay()


	def youLikeHitsLogin(self):
		# Login no site YouLikeHits
		url = 'https://www.youlikehits.com/login.php'
		self.driver.get(url)
		el = self.driver.find_element(By.XPATH, '//*[@id="username"]')
		el.send_keys(self.__settings['YLHUsername'])
		self.delay()

		el = self.driver.find_element(By.XPATH, '//*[@id="password"]')
		el.send_keys(self.__settings['YLHPassword'])
		self.delay()

		self.driver.find_element(By.XPATH, '/html/body/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[2]/td/center/form/table/tbody/tr[3]/td/span/input').click()


	def getStartPoints(self):
		startpointsText = self.getCurrentPoints()
		startpoints = int(startpointsText.replace(',', ''))
		self.startpoints = startpoints
		print(f'Você tem {startpointsText} pontos')


	def getCurrentPoints(self):
		# Pegar a quantidade de pontos atuais
		return self.driver.find_element(By.XPATH, '//*[@id="currentpoints"]').text


	def delay(self, qtdLoops=1):
		# Esperar um tempo antes de fazer próxima ação, simulando um delay humano
		tempos = (0.45, 0.56, 0.55, 0.49, 0.39, 0.36, 0.23, 0.14, 0.31, 0.37, 0.23, 0.21, 0.42)
		for i in range(qtdLoops):
			time.sleep(random.choice(tempos))


	def confirmLogin(self):
		#if self.__settings['headlessmode'] == False:
		if not self.__settings['headlessmode']:
			input('Enter para confirmar Login')

		# Talvez devesse ser um método separado, mas vai aqui mesmo
		self.startpoints = self.getStartPoints()


	def twitterLikes(self):
		"""
		Fazer as ações de like e (talvez) dislike

		Só são possíveis 15 likes por hora e aparecem 9 tweets por páginha
		"""

		url = 'https://www.youlikehits.com/favtweets.php'
		# Controlar quantos likes já foram efetuados
		cont = 15 # Mudar para 0 quando parar os testes

		runningFree = True
		# I'm running wild, I'm running free
		# I'm running free, yeah
		# I'm running free
		# I'm running free, yeah
		# Oh, I'm running free
		# Get out of my way, hey

		while runningFree:
			self.driver.get(url)
			mainWindow = self.driver.window_handles[0]

			try:
				# Certificar que tem tag iframe na página e pegar todas
				iframes = WebDriverWait(self.driver, 4).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'iframe')))
				# Pegar também o conteúdo de cada tweet
				tweetElements = WebDriverWait(self.driver, 4).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'i')))
			except TimeoutException:
				# Significa que o próprio site já informa do limite atingido
				self.log('Atingiu o limite de 15 likes\nVolte daqui a 1h')
				break

			for i in iframes:
				# Cada iframe é acessado
				self.driver.switch_to.frame(i)

				# Encontrar o botão de like da tag iframe
				likeButton = self.driver.find_element(By.LINK_TEXT, 'Like')
				likeButton.click()
				self.delay(2)

				# Mudar para a janela popup que se abre
				popup = self.driver.window_handles[-1]
				self.driver.switch_to.window(popup)
				self.delay(2)

				if self.tweetHasBannedWords():
					# Tem que dar skip se for um tweet nojento
					self.skipTweet(i)
					continue

				try:
					"""
					Neste caso, não vamos esperar muito caso haja algum erro
					10 segundos parece suficiente, e chamamos a classe WebDriverWait diretamente
					em vez de usar o atributo self._wait
					"""
					# Botão LIKE do tweet na janela popup
					twitterLikeButton = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/div[1]')))
				except TimeoutException:
					"""
					Se der erro, o elemento não existe
					Pode ser perfil suspenso, deletado ou o tweet não existe mais
					Então voltamos e pulamos o perfil
					"""
					# Pular perfil, 'i' é a tag iframe 'WebElement'
					self.skipTweet(i)
					# Por garantia, mudar para a janela principal
					self.driver.switch_to.window(mainWindow)
					self.delay(2)
					# Ir para o próximo elemento do loop
					continue

				"""
				Caso tenha passado pelo bloco try
				então vamos dar o like no tweet
				"""
				self.pressIt(twitterLikeButton)
				self.delay(3)

				# Mudar para janela principal e voltar ao iframe
				self.driver.switch_to.window(mainWindow)
				self.driver.switch_to.frame(i)
				# Clicar no botão de like
				confirmButton = self.driver.find_element(By.LINK_TEXT, 'Confirm')
				confirmButton.click()
				# Mudar para o frame pai
				self.driver.switch_to.parent_frame()

				"""
				O elemento com id txtHint existe, mas no início é uma string vazia
				enquanto carrega o texto de sucesso ou fracasso da ação
				Então esperamos até que apareça alguma string dentro deste elemento
				"""
				while 1:
					txtHint = self._wait.until(EC.presence_of_element_located((By.ID, 'txtHint')))
					uhoh = txtHint.text.split('\n')[0].lower().strip()
					self.delay(4)
					# Quando não for mais uma string vazia, quebramos o loop
					if uhoh:
						break

				# Voltar ao popup
				self.driver.switch_to.window(popup)

				if uhoh == 'uh oh':
					# Se o like não foi computado, TIRAMOS O LIKE
					self.dislike()
				else:
					# Se não apareceu mensagem de erro, contamos o sucesso
					cont += 1

				self.delay(3)
				# Fechar janela popup, independente de sucesso ou erro
				self.driver.close()
				# Voltar à janela principal
				self.driver.switch_to.window(mainWindow)
				"""
				Se já fez 15 likes, tá na hora de terminar
				15 likes por hora é uma limitação do próprio twitter
				então pra não dar erros, já terminamos o método
				"""
				if cont >= 15:
					runningFree = False
					self.log('Atingiu o limite de 15 likes\nVolte depois de 1h')
					break


	def twitterFollow(self):
		# Variável para controlar o loop infinito e recarregar a página com mais perfis
		runningFree = True
		url = 'https://www.youlikehits.com/twitter2.php'
		# Acessar página
		self.driver.get(url)
		# Perguntar quantos perfis quer seguir
		# Às vezes são poucos pontos, nem vale a pena
		qtdFollow = self.askUserOption()
		seguidos = 0

		while runningFree:
			# Definir janela principal
			mainWindow = self.driver.window_handles[0]
			# Pegar os botões de follow, confirm e skip
			followButtons, confirmButtons, skipButtons = self.__getTwitterFollowButtons()

			# Loop para cada perfil
			for i in range(len(followButtons)):
				nickname = self.getNickname(followButtons[i])
				self.log(f'Perfil atual: \033[93m{nickname}\033[00m')
				self.delay(3)
				# Clicar no botão de follow no índice i da lista followButtons
				# Este elemento é um WebElement
				followButtons[i].click()
				# Mudar para a janela popup
				popup = self.driver.window_handles[-1]
				self.driver.switch_to.window(popup)
				self.delay(4)

				try:
					# Esperar página de redirecionamento
					WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="autoclick"]/b'))).click()
					self.log('Redirecionando')
				except TimeoutException:
					self.driver.refresh()
					WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="autoclick"]/b'))).click()
					self.log('2 tentativa - redirecionar')
				except:
					self.log('Esperar 5 segundos pra ver se essa merda redireciona')
					time.sleep(5)

				try:
					# Esperar um pouco para renderizar o conteúdo
					self.delay(3)
					WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div[2]/div/div[1]/span')))

					"""
					Algumas vezes pegava o XPATH acima mas não era perfil válido, então ainda temos que checar a string na função perfilExistente
					Todavia, se der exceção no XPATH acima, é um perfil ativo. Pois o mesmo (xpath) só aparece para indicar se o perfil está suspenso ou algo do tipo
					"""
					if not self.__isProfileOK():
						self.delay(4)
						# Fechar janela popup
						self.driver.close()
						# Mudar para janela principal
						self.driver.switch_to.window(mainWindow)
						self.delay(2)
						# Skip neste perfil
						# O mesmo índice se aplica aos botões follow, confirm e skip
						skipButtons[i].click()
						# Pular para o próximo perfil da lista
						continue
					else:
						# Neste caso, encontrou o XPATH mas está vazio (significa que há perfis válidos com esse XPATH) e sua string é vazia
						# Vamos forçar uma exceção
						WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.ID, 'naoExisteNadaAqui')))
						self.log('Tag span encontrada mas vazia')
				except TimeoutException:
					# self.log('Elemento span não encontrado, perfil válido')
					# Neste caso, significa que o perfil é válido
					# Localizar a presença do botão de follow e pressionar
					twitterFollowButton = self._wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/div[1]/div')))
					self.pressIt(twitterFollowButton)
					self.delay(3)
					self.log('Seguindo perfil')
					# Mudar para janela principal
					self.driver.switch_to.window(mainWindow)
					# Clicar no botão confirm
					confirmButtons[i].click()

					# Confirmar se o follow foi computado pelo YLH
					uhoh = self.__confirmSuccessFollow()
					self.delay(4)
					# Voltar ao popup antes de proceder com a ação necessária
					self.driver.switch_to.window(popup)

					if uhoh == 'uh oh':
						self.log('Removendo follow')
						# Dar unfollow pois o YLH não computou
						self.unfollowProfile()
						self.delay(2)

						# Fechar janela popup
						self.driver.close()
						# Mudar para janela principal
						self.driver.switch_to.window(mainWindow)
						# Skip no perfil
						#TODO Talvez seja um erro momentâneo, poderia apenas dar unfollow. Num outro momento pode ser que funcione o follow
						skipButtons[i].click()
					else:
						# Neste caso, computou o follow e só fechamos o popup e mudamos para a janela principal
						self.driver.close()
						self.driver.switch_to.window(mainWindow)
						# Contabilizar o sucesso para finalizar caso haja um limite
						seguidos += 1
						if seguidos == qtdFollow:
							runningFree = False
							break
				except Exception as e:
					"""
					Se, por algum motivo, não aparecer o botão de follow,
					talvez haja algum outro problema que ainda não apareceu nos testes
					"""
					self.log(e)

			# Hora de carregar mais perfis
			if runningFree:
				self.driver.get(url)


	def unfollowProfile(self):
		"""
		Tem uma div que se comporta diferente ao dar unfollow
		2x aconteceu de ter XPATH diferentes
		Então vamos fazer um loop para achar seu número certo
		"""
		for i in range(1, 10):
			try:
				unfollowButton = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div/div/div[1]/div[2]/div[{i}]/div/div/div')))
			except:
				pass
			else:
				self.log(f'div[{i}] - ok')
				break
		
		# Apertar o botão de unfollow
		self.pressIt(unfollowButton)
		self.delay()

		# Clicar no botão de CONFIRMAÇÃO DO UNFOLLOW
		confirmUnfollow = self._wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/div[1]')))
		self.pressIt(confirmUnfollow)


	def getNickname(self, element):
		txt = element.get_attribute('onclick')
		alpha = txt.find('?uname=') + 7
		omega = txt.find("','")
		nick = txt[alpha: omega]
		return '@' + nick


	def __confirmSuccessFollow(self):
		while 1:
			# Pegar a string do elemento com id txtHint
			txtHint = self._wait.until(EC.presence_of_element_located((By.ID, 'txtHint')))
			txtHint = txtHint.text.lower()
			# Quando a string 'verifying' sumir, significa que temos o texto que queremos
			if 'verifying' not in txtHint:
				# Fazemos um split para pegar o texto que importa
				uhoh = txtHint.split('\n')[0].strip()
				break
			# Esperar um pouco antes de checar novamente
			self.delay(2)
		return uhoh


	def __isProfileOK(self):
		# Verificar se o perfil é válido
		# Aumentar a janela para renderizar mais elementos
		self.driver.set_window_size(1000, 700)
		listSpan = self.driver.find_elements(By.TAG_NAME, 'span')
		for span in listSpan:
			txt = span.text.lower().strip()
			if txt == 'account suspended':
				self.log('Perfil suspenso')
				return False
			elif txt == "this account doesn’t exist":
				self.log('Perfil não existe')
				return False
			elif 'this account is temporarily restricted' in txt:
				self.log('Perfil com problemas')
				return False
		return True


	def __getTwitterFollowButtons(self):
		# Follow buttons
		fButtons = self._wait.until(EC.presence_of_all_elements_located((By.LINK_TEXT, 'Follow')))
		# Confirm buttons
		cButtons = self._wait.until(EC.presence_of_all_elements_located((By.LINK_TEXT, 'Confirm')))
		# Skip buttons
		sButtons = self._wait.until(EC.presence_of_all_elements_located((By.LINK_TEXT, 'skip')))

		return fButtons, cButtons, sButtons


	def askUserOption(self):
		# Perguntar quantos perfis vai seguir ou ao infinito e além (mentira, limite é 1 milhão)
		while 1:
			op = input('Quantos perfis seguir [0 para seguir sem parar]: ')
			if op.isnumeric():
				op = int(op)
				break
		if op == 0:
			return 1000000
		else:
			return op


	def pressIt(self, button):
		# Simular ação clicar e segurar
		action = webdriver.common.action_chains.ActionChains(self.driver)
		action.click_and_hold(button).perform()
		self.delay()
		action.release().perform()


	def dislike(self):
		#TODO tava dando erro nessa parte
		# Encontrar o coração do like e remover a curtida
		dislikeButton = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/section/div/div/div[1]/div/div[1]/article/div/div/div/div[3]/div[5]/div/div[3]/div')
		dislikeButton.click()


	def skipTweet(self, frame):
		# Fechar popup e voltar à janela principal
		self.driver.close()
		self.driver.switch_to.window(mainWindow)
		# Voltar ao iframe, depois para o parent_frame e clicar no botão skip
		self.driver.switch_to.frame(frame)
		self.driver.switch_to.parent_frame()
		# Elemento do botão skip e click
		skipButton = self.driver.find_element(By.LINK_TEXT, 'skip')
		skipButton.click()


	def tweetHasBannedWords(self):
		"""
		No twitter há pessoas que não prestam, então checar se o tweet tem palavras que referem a crime ou algo ilegal e (seria bom uma função para denunciar esses perfis automaticamente) skip neste tweet logo
		TODO
		Seria interessante usar alguma api de reconhecimento de frases e tal
		Tem a lib spacy
		"""
		tweet = self.driver.title
		banned = ['ass rape', 'rape', 'child porn', 'rapist', 'pedo']
		for word in banned:
			if word in tweet:
				return True
		return False


	def log(self, msg):
		"""
		Digitar log é mais rápido que print (hahaha)
		Oops, era quando usava só módulos. Agora com self.log fica mais longo
		Só para entender onde o código está sendo executado
		TODO Talvez implementar código para salvar um arquivo para análises futuras
		"""
		print(msg)


	def goodbye(self):
		# Finalizar o driver
		self.driver.quit()


	def showEarnedPoints(self):
		endpointsText = self.getCurrentPoints()
		endpoints = int(endpointsText.replace(',', ''))
		total = endpoints - self.startpoints
		self.log(f'Pontos ganhos nesta sessão: {total:,}')


	def bonusPoints(self):
		#TODO
		# Pegar os bonus quando tiver feito 75 hits no dia
		bonus_points = 'https://www.youlikehits.com/bonuspoints.php'
		pass
