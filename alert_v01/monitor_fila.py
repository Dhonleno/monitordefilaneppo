import time
import pyttsx3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from credenciais import USUARIO, SENHA

def login_e_abrir_dashboard(driver):
    print("Iniciando login...")
    driver.get("https://multsoft.neppo.com.br/chat/#/login")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    print("Campo de usuário encontrado. Preenchendo login...")
    driver.find_element(By.NAME, "username").send_keys(USUARIO)
    driver.find_element(By.NAME, "password").send_keys(SENHA)
    btn_login = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.TAG_NAME, "button"))
    )
    btn_login.click()
    print("Login enviado. Aguardando redirecionamento...")
    time.sleep(7)
    print(f"URL atual após login: {driver.current_url}")
    erro_login = None
    try:
        erro_login = driver.find_element(By.CSS_SELECTOR, '.alert-danger, .alert-error, .error-message')
    except Exception:
        pass
    if erro_login:
        print("Erro de login detectado:")
        print(erro_login.text)
        print(f"HTML da página após login:\n{driver.page_source[:2000]}")
        return False
    driver.get("https://multsoft.neppo.com.br/chat/#/dashboard")
    print("Aguardando dashboard carregar...")
    time.sleep(7)
    # Seleciona a aba "Canais" no dashboard usando o atributo data-cy
    try:
        aba_canais = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "section[data-cy='nav-channel']"))
        )
        aba_canais.click()
        print("Aba 'Canais' selecionada.")
        time.sleep(2)
    except Exception as e:
        print(f"Não foi possível selecionar a aba 'Canais': {e}")
    return True

def buscar_clientes_em_espera_dashboard(driver):
    nucleos = []
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".card-group-wrapper"))
        )
        grupos = driver.find_elements(By.CSS_SELECTOR, ".card-group-wrapper")
        for grupo in grupos:
            try:
                titulo = grupo.find_element(By.CSS_SELECTOR, ".card-group-title span").text.strip()
            except Exception:
                continue
            if titulo.strip().lower() == "em espera":
                empty = grupo.find_elements(By.CSS_SELECTOR, "span.empty-cards")
                if empty:
                    continue
                artigos = grupo.find_elements(By.CSS_SELECTOR, "article.card-status-wait")
                for art in artigos:
                    try:
                        p = art.find_element(By.CSS_SELECTOR, "p.group-text, p.group-text.ng-binding")
                        nucleo = p.get_attribute("title")
                        if nucleo:
                            nucleos.append(nucleo)
                    except Exception:
                        continue
    except Exception as e:
        print(f"Erro ao buscar clientes em espera: {e}")
    return nucleos

def obter_clientes_em_espera(driver):
    try:
        nucleos = buscar_clientes_em_espera_dashboard(driver)
        print("Núcleos encontrados:", nucleos)
        return nucleos
    except Exception as e:
        print(f"Erro ao obter clientes em espera: {e}")
        return []

def anunciar_cliente(nucleo, voz_id=None):
    # Extrai apenas o nome do núcleo, removendo o número de celular se houver
    nome_nucleo = nucleo.split(' - ')[0] if ' - ' in nucleo else nucleo
    # Corrige pronúncia específica para núcleos
    if nome_nucleo.strip().lower() == "reproducao":
        nome_nucleo = "Reprodução"
    elif nome_nucleo.strip().lower() == "conexao de bastao e balanca":
        nome_nucleo = "Conexão de bastão e balança"
    elif nome_nucleo.strip().lower() == "pmg e comunicacao para associacao":
        nome_nucleo = "PMG e Comunicação para Associação"
    engine = pyttsx3.init()
    if voz_id is not None:
        voices = engine.getProperty('voices')
        if 0 <= voz_id < len(voices):
            engine.setProperty('voice', voices[voz_id].id)
    engine.say(f"Atenção! Cliente aguardando no núcleo {nome_nucleo}.")
    engine.runAndWait()

def listar_vozes():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for idx, voice in enumerate(voices):
        print(f"Voz {idx}: {voice.name} - {voice.id}")
    engine.stop()

def buscar_status_grupos_dashboard(driver):
    status_grupos = []
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".agents-dashboard-attendance-list .card-group-wrapper"))
        )
        grupos = driver.find_elements(By.CSS_SELECTOR, ".agents-dashboard-attendance-list .card-group-wrapper")
        for grupo in grupos:
            try:
                titulo = grupo.find_element(By.CSS_SELECTOR, ".card-group-title span").text.strip()
            except Exception:
                continue
            # Atendendo
            atendendo_cards = grupo.find_elements(By.CSS_SELECTOR, "article.card-status-attendance")
            atendendo_infos = []
            for card in atendendo_cards:
                try:
                    group_text = card.find_element(By.CSS_SELECTOR, "p.group-text").get_attribute("title")
                    agent_text = card.find_element(By.CSS_SELECTOR, "p.agent-text").get_attribute("title")
                    atendendo_infos.append(f"{group_text} ({agent_text})")
                except Exception:
                    continue
            # Pausados
            pausados_cards = grupo.find_elements(By.CSS_SELECTOR, "article.card-status-pause")
            pausados_infos = []
            for card in pausados_cards:
                try:
                    group_text = card.find_element(By.CSS_SELECTOR, "p.group-text").get_attribute("title")
                    agent_text = card.find_element(By.CSS_SELECTOR, "p.agent-text").get_attribute("title")
                    pausados_infos.append(f"{group_text} ({agent_text})")
                except Exception:
                    continue
            # Em espera
            espera_cards = grupo.find_elements(By.CSS_SELECTOR, "article.card-status-wait")
            espera_infos = []
            for card in espera_cards:
                try:
                    group_text = card.find_element(By.CSS_SELECTOR, "p.group-text").get_attribute("title")
                    espera_infos.append(group_text)
                except Exception:
                    continue
            # Disponíveis
            disponiveis_cards = grupo.find_elements(By.CSS_SELECTOR, "article.card-status-avaliable")
            disponiveis_infos = []
            for card in disponiveis_cards:
                try:
                    group_text = card.find_element(By.CSS_SELECTOR, "p.group-text").get_attribute("title")
                    agent_text = card.find_element(By.CSS_SELECTOR, "p.agent-text").get_attribute("title")
                    disponiveis_infos.append(f"{group_text} ({agent_text})")
                except Exception:
                    continue
            status_grupos.append({
                'grupo': titulo,
                'atendendo': len(atendendo_cards),
                'atendendo_infos': atendendo_infos,
                'pausados': len(pausados_cards),
                'pausados_infos': pausados_infos,
                'em_espera': len(espera_cards),
                'espera_infos': espera_infos,
                'disponiveis': len(disponiveis_cards),
                'disponiveis_infos': disponiveis_infos
            })
    except Exception as e:
        print(f"Erro ao buscar status dos grupos: {e}")
    return status_grupos

def monitorar_fila():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Descomente para rodar em modo visível para debug
    # Usa Selenium Manager para baixar e gerenciar o ChromeDriver automaticamente
    driver = webdriver.Chrome(options=chrome_options)
    try:
        if not login_e_abrir_dashboard(driver):
            print("Falha no login. Encerrando monitoramento.")
            return
        clientes_anteriores = set()
        avisos_ativos = {}
        ordem_clientes = []
        nucleos_nao_notificar = [
            'administrativo',
            'comercial',
            'projetos e treinamentos'
        ]
        while True:
            clientes_atuais = set([
                nucleo for nucleo in buscar_clientes_em_espera_dashboard(driver)
                if nucleo and nucleo.split(' - ')[0].strip().lower() not in nucleos_nao_notificar
            ])
            novos_clientes = clientes_atuais - clientes_anteriores
            clientes_removidos = clientes_anteriores - clientes_atuais
            # Remove clientes que saíram da fila
            for cliente in clientes_removidos:
                avisos_ativos.pop(cliente, None)
                if cliente in ordem_clientes:
                    ordem_clientes.remove(cliente)
            # Adiciona novos clientes ao final da ordem
            for cliente in novos_clientes:
                ordem_clientes.append(cliente)
                avisos_ativos[cliente] = time.time() + 1.5  # espera 1.5s para primeira notificação
            # Garante que só clientes atuais estejam na ordem e nos avisos_ativos
            ordem_clientes = [c for c in ordem_clientes if c in clientes_atuais]
            avisos_ativos = {c: avisos_ativos[c] for c in ordem_clientes}
            # Notifica por ordem, um de cada vez, repetindo sucessivamente
            if ordem_clientes:
                cliente_atual = ordem_clientes[0]
                agora = time.time()
                if agora >= avisos_ativos.get(cliente_atual, 0):
                    anunciar_cliente(cliente_atual)
                    avisos_ativos[cliente_atual] = agora + 5
                # Rotaciona a ordem para o próximo cliente na próxima iteração
                ordem_clientes = ordem_clientes[1:] + [cliente_atual]
            clientes_anteriores = clientes_atuais
            time.sleep(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    listar_vozes()
    # monitorar_fila()  # Comente esta linha para testar as vozes
    

    
    monitorar_fila()
