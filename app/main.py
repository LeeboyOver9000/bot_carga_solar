import os
import logging

from dotenv import load_dotenv, find_dotenv

from datetime import datetime, timedelta
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options


from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException, TimeoutException

dir_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(dir_path)

# dia_da_carga = datetime(day=27, month=5, year=2022)
dia_da_carga = datetime.now() - timedelta(days=3)
dia_da_carga_formatado = f'{datetime.strftime(dia_da_carga, "%d/%m/%Y")} 00:00'

log_formart = '%(asctime)s - %(message)s'

logging.basicConfig(filename='output.log',
                    filemode='w',
                    level=logging.INFO,
                    format=log_formart)

logger = logging.getLogger('root')


def login(usuario: str, senha: str) -> WebDriver:
    """Faz o login para entrar no formulário de carga."""
    url = f'http://{usuario}:{senha}@200.129.43.116/Solar2SI3/Batch/Batches.aspx'

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('--dns-prefetch-disable')

    chrome_service = Service(ChromeDriverManager().install())
    browser = Chrome(service=chrome_service, options=options)
    browser.get(url)
    return browser


def resultado_popup(mensagem: str, browser: WebDriver):
    """Ler o conteúdo do popup, escreve o conteúdo em output.log e no console."""
    original_window = browser.current_window_handle
    mensagem_formatada = f'{mensagem} ({dia_da_carga_formatado})'

    try:
        # Espera até 1 hora (3600 segundos) pelo resultado
        wait = WebDriverWait(browser, timeout=3600)
        wait.until(EC.number_of_windows_to_be(2))

        for window_handle in browser.window_handles:
            if window_handle != original_window:
                browser.switch_to.window(window_handle)

                wait.until(EC.presence_of_element_located((By.ID, 'lbLog')))
                result_text = browser.find_element(By.ID, 'lbLog').text
                if not result_text:
                    mensagem_formatada += ' Ok!'
                    logger.info(mensagem_formatada)
                    print(mensagem_formatada)
                else:
                    mensagem_formatada += f': {result_text}'
                    logger.error(mensagem_formatada)
                    print(mensagem_formatada)

                browser.close()
    except NoSuchElementException as err:
        mensagem_formatada += f': {err}'
        logger.error(mensagem_formatada)
        print(mensagem_formatada)
    except TimeoutException:
        logger.error(
            f'Demorou mais de 1 hora pra fazer a {mensagem.lower()}.')
        print(
            f'Demorou mais de 1 hora pra fazer a {mensagem.lower()}.')

    browser.switch_to.window(original_window)


def carga_disciplinas(browser: WebDriver):
    """Realiza a carga das disciplinas usando o dia da carga."""
    wait = WebDriverWait(browser, timeout=30)
    checkbox = wait.until(EC.element_to_be_clickable((By.ID, 'distancia')))
    if checkbox.get_attribute('checked'):
        checkbox.click()

    browser.find_element(By.ID,
                         'txtAltTurmaDisc').send_keys(dia_da_carga_formatado)
    browser.find_element(By.ID, 'btDisciplinas').click()

    resultado_popup('Carga das Disciplinas', browser)

    browser.find_element(By.ID, 'txtAltTurmaDisc').clear()


def carga_turmas(browser: WebDriver):
    """Realiza a carga das turmas usando o dia da carga."""
    wait = WebDriverWait(browser, timeout=30)
    checkbox = wait.until(
        EC.element_to_be_clickable((By.ID, 'turma_distancia')))
    if checkbox.get_attribute('checked'):
        checkbox.click()

    browser.find_element(By.ID, 'txDtTurma').send_keys(
        dia_da_carga_formatado)
    browser.find_element(By.ID, 'btTurmas').click()

    resultado_popup('Carga das Turmas', browser)

    browser.find_element(By.ID, 'txDtTurma').clear()


def carga_matriculas_presencial(browser: WebDriver):
    """Realiza a carga das turmas prenciais usando o dia da carga."""
    wait = WebDriverWait(browser, timeout=30)
    checkbox = wait.until(
        EC.element_to_be_clickable((By.ID, 'mat_distancia')))
    if checkbox.get_attribute('checked'):
        checkbox.click()

    browser.find_element(By.ID, 'txtAltTurma').send_keys(
        dia_da_carga_formatado)
    browser.find_element(By.ID, 'btMatriculas').click()

    resultado_popup('Carga das Matrículas - Alteração das Turmas', browser)

    browser.find_element(By.ID, 'txtAltTurma').clear()
    browser.find_element(By.ID,
                         'txDtMatricula').send_keys(dia_da_carga_formatado)
    browser.find_element(By.ID, 'btMatriculas').click()

    resultado_popup('Carga das Matrículas - Presenciais', browser)

    browser.find_element(By.ID, 'txtAltTurma').clear()
    browser.find_element(By.ID, 'txDtMatricula').clear()


def carga_matriculas_distancia(browser: WebDriver):
    """Realiza a carga das turmas EAD sem passar dia pra carga."""
    wait = WebDriverWait(browser, timeout=30)
    checkbox = wait.until(EC.element_to_be_clickable((By.ID, 'mat_distancia')))
    if not checkbox.get_attribute('checked'):
        checkbox.click()

    browser.find_element(By.ID, 'btMatriculas').click()

    resultado_popup('Carga das Matrículas - A Distância', browser)


def ler_resultado_log(arquivo_de_log: str) -> str:
    resultado = ''
    with open(arquivo_de_log, 'r') as log:
        for linha in log:
            resultado += linha
    return resultado


load_dotenv(find_dotenv())

usuario = os.environ.get("USUARIO")
senha = os.environ.get("SENHA")

if __name__ == '__main__':
    browser: WebDriver = login(usuario, senha)

    carga_disciplinas(browser)
    carga_turmas(browser)
    carga_matriculas_presencial(browser)
    # carga_matriculas_distancia(browser)

    browser.quit()
