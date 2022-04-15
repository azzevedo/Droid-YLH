import time
import random
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException



def log(msg):
	# Log é mais curto que print para digitar  hahahaha
	# Só para entender onde o código está sendo executado
	# Talvez implementar salvar um arquivo para futuras análises
	print(msg)



def esperar(qtdLoops):
	# Esperar um tempo antes de fazer próxima ação
	# Tempos para simular ação humana e dar um tempo para os elementos carregarem na página
	tempos = (0.45, 0.56, 0.55, 0.49, 0.39, 0.36, 0.23, 0.14, 0.31, 0.37, 0.23, 0.21, 0.42)
	for i in range(qtdLoops):
		time.sleep(random.choice(tempos))



def importSettings():
	# Abrir configurações de login
	settingU = json.load(open('twitter.json'))
	jcopy = json.dumps(settingU)
	setting = json.loads(jcopy)
	return setting



def getStartPoints(driver):
	# Pegar a quantidade de pontos atuais
	startpointsText = driver.find_element(By.XPATH, '//*[@id="currentpoints"]').text
	startpoints = int(startpointsText.replace(',', ''))
	print(f'Você tem {startpoints:,} pontos')
	return startpoints



def showEarnedPoints(driver, startpoints):
	# Mostrar total de pontos ganhos
	endpointsText = driver.find_element(By.XPATH, '//*[@id="currentpoints"]').text
	endpoints = int(endpointsText.replace(',', ''))
	total = endpoints - startpoints
	# os.system('clear')
	print(f'Pontos ganhos: {total:,}')



def twitterLogin(driver, settings, url, wait):
	# Login no Twitter
	driver.get(url)
	time.sleep(7)

	########   Elemento de Username   ########
	el = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[5]/label/div/div[2]/div/input')))
	el.send_keys(settings["twitterUsername"])
	esperar(1)

	# Botão de avançar
	el = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[6]/div')))
	el.click()
	esperar(1)

	########   Elemento de senha   ########
	el = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')))
	el.send_keys(settings["twitterPassword"])
	esperar(1)

	# Login com senha inserida
	el = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div')))
	el.click()
	esperar(1)



def youLikeHitsLogin(driver, setting, url):
	# Login no site YouLikeHits
	driver.get(url)
	driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(setting["YLHUsername"])
	esperar(1)

	driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(setting["YLHPassword"])
	esperar(1)

	driver.find_element(By.XPATH, '/html/body/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[2]/td/center/form/table/tbody/tr[3]/td/span/input').click()



def twitterLikes(driver, url, wait):
	# Só são possíveis 15 likes e aparecem 9 por página
	# Contar quantos já foram feitos para finalizar a ação dos likes
	cont = 0
	# Simular ação clicar e segurar
	action = webdriver.common.action_chains.ActionChains(driver)

	runningFree = True
	# I'm running wild, I'm running free
	# I'm running free, yeah
	# I'm running free
	# I'm running free, yeah
	# Oh, I'm running free
	# Get out of my way, hey

	while runningFree:
		driver.get(url)
		# Janela principal
		mainWindow = driver.window_handles[0]

		try:
			# Certificar que tem tag iframe na página e pegar todas
			iframes = WebDriverWait(driver, 4).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'iframe')))
		except TimeoutException:
			# Significa que o próprio site já informa do limite atingido
			print("Atingiu o limite de 15 likes")
			print("Volte daqui a 1h para mais 15 likes")
			break

		#TODO apagar
		# Redundante, já que tem o except acima
		'''
		if not iframes:
			# Se não encontrar a tag iframe, significa que já fez os 15 likes permitidos por hora
			print('ATINGIU O LIMITE DE 15 LIKES POR HORA')
			break
		'''

		for i in iframes:
			# Cada iframe é acessado
			driver.switch_to.frame(i)

			# Encontrar o botão de like da tag iframe
			likeButton = driver.find_element(By.LINK_TEXT, 'Like')
			likeButton.click()
			esperar(2)

			# Mudar para a janela popup que se abre
			popup = driver.window_handles[-1]
			driver.switch_to.window(popup)
			esperar(2)

			try:
				# Neste caso, não quero esperar muito caso haja algum erro
				# 10 segundos parece suficiente, e chamamos a classe diretamente
				# em vez de usar a instância 'wait' recebida como argumento da função
				# Botão LIKE para curtir o tweet na janela popup
				twitterLikeButton = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/div[1]')))
			except TimeoutException:
				# Se der erro, o elemento não existe
				# O perfil deve estar suspenso, deletado ou o tweet não existe mais
				# Simplesmente voltar e pular esse perfil
				# Fechar janela popup
				driver.close()
				# Voltar à janela principal
				driver.switch_to.window(mainWindow)
				# Voltar ao iframe
				driver.switch_to.frame(i)
				# Mudar para o frame parent onde se encontra o botão de skip
				driver.switch_to.parent_frame()
				# Pular o perfil
				skip = driver.find_element(By.LINK_TEXT, 'skip')
				skip.click()
				# Por garantia, mudar para janela principal
				driver.switch_to.window(mainWindow)
				esperar(2)
				# Ir ao próximo elemento do loop
				continue

			# Caso tenha passado pelo bloco 'try'
			# Confirmar ação com clique, segura e solta
			action.click_and_hold(twitterLikeButton).perform()
			esperar(1)
			action.release().perform()
			esperar(3)

			# Mudar para janela principal
			driver.switch_to.window(mainWindow)
			# Voltar ao iframe
			driver.switch_to.frame(i)
			# Botão para confirmar o like
			confirmButton = driver.find_element(By.LINK_TEXT, 'Confirm')
			confirmButton.click()
			# Mudar para o frame pai
			driver.switch_to.parent_frame()

			# O elemento com id txtHint existe, mas no início é vazio '' e depois vai ficar o texto de sucesso ou fracasso da ação
			# Como diferenciar isso?
			# Para a string vazia, pode ser um while True para quando a string não for mais vazia
			# O while serve, já que depois de clicar em confirmar, esse elemento fica carregando até aparecer a mensagem de confirmação do like ou não
			while 1:
				txtHint = wait.until(EC.presence_of_element_located((By.ID, 'txtHint')))
				uhoh = txtHint.text.split('\n')[0].lower().strip()
				esperar(4)
				# Quando não for mais uma string vazia, quebramos o loop
				if uhoh:
					break

			# Se não foi computado, voltamos para o popup, TIRAMOS O LIKE e fechamos
			# Voltar ao popup
			driver.switch_to.window(popup)

			if uhoh == 'uh oh':
				# Encontrar o coração do like e remover a curtida
				removeLike = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/section/div/div/div[1]/div/div[1]/article/div/div/div/div[3]/div[5]/div/div[3]')
				removeLike.click()
			else:
				# Se não apareceu a mensagem de erro
				# Contamos o sucesso
				cont += 1

			esperar(3)
			# Fechar janela popup, independente de sucesso ou erro no like
			driver.close()
			# Voltar o foco do driver para a janela principal
			driver.switch_to.window(mainWindow)

			# Checar se obteve 15 likes bem sucedidos
			# (limitação do próprio twitter só permitir 15 likes por hora)
			# Quebar o laço 'for' e setar 'runningFree' como False para sair do 'while'
			if cont == 15:
				runningFree = False
				print("Atingiu o limite de 15 likes")
				print("Volte daqui a 1h para mais 15 likes")
				break




def findUnfollowButton(driver):
	# Tem uma div que se comporta diferente ao dar unfollow
	# 2x aconteceu de ter XPATH diferentes
	# Então vamos fazer um loop para achar seu número certo
	for i in range(1, 10):
		try:
			ub = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div/div/div[1]/div[2]/div[{i}]/div/div/div')))
		except:
			log(f'div[{i}]')
		else:
			break
	return ub



def bonusPoints(driver, url):
	#TODO implementar esta função
	driver.get(url)
	# Checar se o botão existe. Se está ativo.



def getUserOption():
	while 1:
		op = input('Quantos perfis seguir [0 para seguir sem parar]: ')
		if op.isnumeric():
			op = int(op)
			break
	if op == 0:
		return 1000000
	else:
		return op



def pressIt(driver, element):
	# TODO
	# Implemtar o action aqui para reduzir o código duplicado
	# nas funções de like e follow
	# action = webdriver.common.action_chains.ActionChains(driver)
	pass



def perfilExistente(driver):
	# Verificar se o perfil é válido
	driver.set_window_size(1000, 700)
	listSpan = driver.find_elements(By.TAG_NAME, 'span')
	for span in listSpan:
		txt = span.text.lower().strip()
		if txt == 'account suspended' or txt == "this account doesn’t exist" or 'this account is temporarily restricted' in txt:
			return False
	return True



def twitterFollow(driver, url, wait):
	# Loop infinito para recarregar a página com mais perfis
	# TODO
	# Talvez implementar um input com a quantidade de perfis que queira seguir
	runningFree = True
	qtdFollow = getUserOption()
	seguidos = 0

	while runningFree:
		# Acessar a página
		driver.get(url)
		# Definir janela principal
		mainWindow = driver.window_handles[0]
		# Definir ação para clicar quando necessário
		action = webdriver.common.action_chains.ActionChains(driver)

		# Pegar os botões de follow, confirmação e skip
		followButtons = wait.until(EC.presence_of_all_elements_located((By.LINK_TEXT, 'Follow')))
		confirmButtons = wait.until(EC.presence_of_all_elements_located((By.LINK_TEXT, 'Confirm')))
		skipButtons = wait.until(EC.presence_of_all_elements_located((By.LINK_TEXT, 'skip')))

		# Loop for para cada perfil
		for i in range(len(followButtons)):
			esperar(3)
			# Clicar no botão de follow no índice i da lista followButtons
			followButtons[i].click()
			# Mudar para a janela popup
			popup = driver.window_handles[-1]
			driver.switch_to.window(popup)
			# 'Setar' tamanho da janela popup para ver o elemento pois às vezes não aparece no tamanho original
			#esperar(2)
			#driver.set_window_size(1000, 700)
			esperar(4)

			try:
				# Esperar página de redirecionamento
				#wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="autoclick"]/b'))).click()
				WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="autoclick"]/b'))).click()
				log('Redirecionando')
			except TimeoutException:
				driver.refresh()
				#wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="autoclick"]/b'))).click()
				WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="autoclick"]/b'))).click()
				log('2 tentativa - redirecionar')
			except:
				log('Esperar 5 segundos')
				time.sleep(5)

			try:
				# Esperar um pouco para o elemento renderizar por completo
				#TODO só tá pegando texto vazio, talvez melhor tirar o if
				esperar(3)
				# Checar se o perfil é inexistente através deste elemento
				WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div[2]/div/div[1]/span')))
				# Algumas vezes pegava o XPATH acima mas não era perfil válido, então ainda temos que checar a string na função perfilExistente
				# Todavia, se der exceção no XPATH acima, é um perfil ativo
				if not perfilExistente(driver):
					log('Perfil não existe!')
					esperar(4)
					# Fechar janela popup
					driver.close()
					# Mudar para janela principal
					driver.switch_to.window(mainWindow)
					# Dar skip neste perfil
					# O mesmo índice se aplica para botões follow, confirm e skip
					esperar(2)
					skipButtons[i].click()
					# Pular para próximo perfil no loop
					continue
				else:
					# Neste caso, encontrou o XPATH mas está vazio (significa que há perfis válidos com esse XPATH) e sua string é vazia
					# Vamos forçar uma exceção
					WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, 'naoExisteNadaAqui')))
					log('Span encontrado mas vazio')
			except TimeoutException:
				log('Elemento span não encontrado')
				esperar(2)
				# Neste caso, significa que o perfil é válido
				# Localizar a presença do botão de follow
				twitterFollowButton = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/div[1]/div')))
				# Clicar no botão, segurar e soltar
				action.click_and_hold(twitterFollowButton).perform()
				esperar(1)
				action.release().perform()
				esperar(3)
				log('Seguindo Perfil')
				# Mudar para janela principal
				driver.switch_to.window(mainWindow)
				# Clicar no botão confirm
				confirmButtons[i].click()

				# Confirmar se o follow foi computado pelo ylh
				while 1:
					txtHint = wait.until(EC.presence_of_element_located((By.ID, 'txtHint')))
					txtHint = txtHint.text.lower()
					if 'verifying' not in txtHint:
						uhoh = txtHint.split('\n')[0].strip()
						break
					esperar(2)

				esperar(4)
				# Voltar ao popup para fechar ou dar unfollow e fechar
				driver.switch_to.window(popup)

				if uhoh == 'uh oh':
					log('Removendo follow')
					# Dar unfollow pois o ylh não computou
					#unfollowButton = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div/div/div[1]/div[2]/div[3]/div/div/div')))
					unfollowButton = findUnfollowButton(driver)
					action.click_and_hold(unfollowButton).perform()
					esperar(1)
					action.release().perform()
					esperar(1)

					# Confirmar unfollow
					confirmUnfollow = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/div[1]')))
					action.click_and_hold(confirmUnfollow).perform()
					esperar(1)
					action.release().perform()

					esperar(2)
					# Fechar janela popup
					driver.close()
					# Mudar para janela principal
					driver.switch_to.window(mainWindow)
					# Dar skip nesse perfil
					skipButtons[i].click()
				else:
					driver.close()
					driver.switch_to.window(mainWindow)
					#TODO se for implementar contagem de sucesso, é aqui
					seguidos += 1
					if seguidos == qtdFollow:
						runningFree = False
						break
			except Exception as e:
				# Se, por algum motivo, não aparecer o botão de follow,
				# talvez tenha algum outro problema com o perfil
				print(e)
