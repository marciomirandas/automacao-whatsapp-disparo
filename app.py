# Importa as bibliotecas
import time
import os
import json
import sys
import sqlite3
import keyboard

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager

from selenium.webdriver.chrome import service as OperaService
from webdriver_manager.opera import OperaDriverManager


# Conecta ao banco de dados
try:
    conexao = sqlite3.connect('arquivos/banco.db')

    # Cria um cursor para executar comandos SQL
    cursor = conexao.cursor()

    # Cria uma tabela
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contatos (
            id INTEGER PRIMARY KEY,
            contato TEXT
        )
    ''')
except:
    print('Erro ao conectar ao banco de dados')
    time.sleep(30)
    sys.exit()


# Abre o arquivo json
try:
    with open('arquivos/dados.json', encoding="utf-8-sig") as file:
        data = json.load(file)

    grupo_json = data['grupo']
    mensagem_json = data['mensagem']
    tempo_json = float(data['tempo'])
    navegador_json = data['navegador']
    administrador_json = data['administrador']
except:
    print('Erro ao abrir o arquivo dados.json')
    time.sleep(30)
    sys.exit()


# Início do programa
try:
    whatsapp = 'https://web.whatsapp.com/'
    caminho_pasta_atual = os.getcwd()

    if navegador_json.lower() == 'c':
        
        options = ChromeOptions()
        options.add_argument("--profile-directory=Default")
        options.add_argument(f"--user-data-dir={caminho_pasta_atual}/arquivos/cookies")

        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    elif navegador_json.lower() == 'e':
        
        options = EdgeOptions()
        options.add_argument("--profile-directory=Default")
        options.add_argument(f"--user-data-dir={caminho_pasta_atual}/arquivos/cookies")

        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
    
    elif navegador_json.lower() == 'f':

        options = FirefoxOptions()
        #options.add_argument("--profile-directory=Default")
        options.add_argument(f"--user-data-dir={caminho_pasta_atual}/arquivos/cookies")

        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)

    elif navegador_json.lower() == 'o':

        webdriver_service = OperaService.Service(OperaDriverManager().install())
        webdriver_service.start()

        options = webdriver.ChromeOptions()
        options.add_argument("--profile-directory=Default")
        options.add_argument(f"--user-data-dir={caminho_pasta_atual}/arquivos/cookies")
        options.add_experimental_option('w3c', True)

        driver = webdriver.Remote(webdriver_service.service_url, options=options)
                
    driver.maximize_window()
    driver.get(whatsapp)
except:
    print('Erro ao instalar os drivers')
    time.sleep(30)
    sys.exit()


while True:

    # Verifica se o whatsapp está logado
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'app')))
        app = driver.find_element(By.ID, 'app')
        side = app.find_element(By.ID, 'side')
        conversas = side.find_elements(By.CLASS_NAME, '_21S-L')
    except:
        time.sleep(5)
        continue

    # Itera as conversas encontradas
    parar_conversa = False
    for conversa in conversas:

        try:
            grupo = conversa.find_element(By.TAG_NAME, 'span')
            grupo.text
        except:
            continue
        
        # Verifica o grupo
        if grupo.text == grupo_json:
            try:
                grupo.click()
                
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'main')))
                main = driver.find_element(By.ID, 'main')
                mensagens = main.find_elements(By.CLASS_NAME, '_1sykI')
            except:
                break

            for mensagem in mensagens:
                
                # Verifica se a mensagem é de algum número que entrou
                if 'entrou usando um link' in mensagem.text:
                    try:
                        span = mensagem.find_element(By.TAG_NAME, 'span')
                    except:
                        continue

                    # Verifica se o número começa com +55
                    if span.text[:3] == '+55':
                        try:
                            numero = span.text

                            # Busca no banco o número do contato
                            cursor.execute('SELECT * FROM contatos WHERE contato = (:numero)', {'numero': numero})
                            resultado = cursor.fetchone()
                        except:
                            continue

                        if resultado == None:
                            try:
                                # Clica no cabeçalho do grupo
                                main.find_element(By.CLASS_NAME, '_2au8k').click()
                                
                                # Clica na lupa
                                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.kk3akd72.a3oefunm')))
                                pesquisar = driver.find_elements(By.CSS_SELECTOR, '.kk3akd72.a3oefunm')
                                pesquisar[1].click()
                                time.sleep(tempo_json)

                                # Escreve o número do participante
                                if navegador_json.lower() == 'f':
                                    keyboard.write(numero)
                                else:
                                    div_pesquisar = driver.find_elements(By.CLASS_NAME, '_1EUay')
                                    div_pesquisar[0].find_element(By.CSS_SELECTOR, '.selectable-text.copyable-text.iq0m558w.g0rxnol2').send_keys(numero)
                                    
                                time.sleep(tempo_json)
                                
                                # Seleciona o participante
                                div_participante = driver.find_elements(By.CSS_SELECTOR, '._3YS_f._2A1R8')
                                div_participante[0].find_element(By.CSS_SELECTOR, '.lhggkp7q.ln8gz9je.rx9719la').click()
                                time.sleep(tempo_json)

                                # Abre a conversa
                                participante = driver.find_elements(By.CSS_SELECTOR, '.iWqod._1MZM5._2BNs3')
                                if administrador_json.lower() == 'sim':
                                    participante[3].click()
                                else:
                                    participante[1].click()
                                time.sleep(tempo_json)

                                # Escreve a mensagem
                                if navegador_json.lower() == 'f':
                                    for paragrafo in mensagem_json:
                                        keyboard.write(paragrafo)
                                        actions = ActionChains(driver)
                                        actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).send_keys(Keys.ENTER).key_up(Keys.SHIFT)
                                        actions.perform()
                                else:
                                    enviar = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p')))
                                    for paragrafo in mensagem_json:
                                        enviar.send_keys(paragrafo)
                                        actions = ActionChains(driver)
                                        actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).send_keys(Keys.ENTER).key_up(Keys.SHIFT)
                                        actions.perform()

                                time.sleep(tempo_json)
                                driver.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[2]/button').click()
                                time.sleep(tempo_json)

                                # Insere dados no banco
                                cursor.execute('INSERT INTO contatos (contato) VALUES (:numero)', {'numero': numero})
                                conexao.commit()

                                parar_conversa = True
                                break
                            except:
                                # Aperta ESC cinco vezes para grantir que voltará a tela inicial
                                for i in range(0,5):
                                    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                                    time.sleep(tempo_json)
                                
                                continue

        # Para o for para voltar ao while principal            
        if parar_conversa == True:
            break
                        
    time.sleep(tempo_json)
