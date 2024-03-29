import os
import logging
import yagmail

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

dia_da_carga = datetime.now() - timedelta(days=1)
dia_da_carga_formatado = f'{datetime.strftime(dia_da_carga, "%d/%m/%Y")} 00:00'

log_formart = '%(asctime)s - %(message)s'

logging.basicConfig(
    filename='output.log', filemode='w', level=logging.INFO, format=log_formart
)

logger = logging.getLogger('root')


def login(usuario: str, senha: str) -> WebDriver:
    """Faz o login para entrar no formulário de carga."""
    url = (
        f'http://{usuario}:{senha}@200.129.43.116/Solar2SI3/Batch/Batches.aspx'
    )

    os.environ['WDM_LOG'] = str(logging.NOTSET)
    os.environ['WDM_LOCAL'] = '1'

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


def resultado_popup(mensagem: str, browser: WebDriver) -> None:
    """Ler o conteúdo do popup, escreve o conteúdo em output.log e no console."""
    mensagem_formatada = f'{mensagem} ({dia_da_carga_formatado})'

    try:
        original_window = browser.current_window_handle

        wait = WebDriverWait(browser, timeout=3600)  # Espera até 1 hora
        wait.until(EC.number_of_windows_to_be(2))

        for window_handle in browser.window_handles:
            if window_handle != original_window:
                browser.switch_to.window(window_handle)

                wait.until(EC.presence_of_element_located((By.ID, 'lbLog')))
                result_text = browser.find_element(By.ID, 'lbLog').text
                if not result_text:
                    mensagem_formatada += ' Ok!'
                    logger.info(mensagem_formatada)
                else:
                    mensagem_formatada += f': {result_text}'
                    logger.error(mensagem_formatada)

                browser.close()

        browser.switch_to.window(original_window)
    except NoSuchElementException as err:
        mensagem_formatada += f': {err}'
        raise NoSuchElementException(mensagem_formatada)
    except TimeoutException:
        mensagem_formatada = f'A execução foi abortada porque demorou mais de 1 hora pra fazer a {mensagem.lower()}.'
        raise TimeoutException(mensagem_formatada)


def carga_disciplinas(browser: WebDriver) -> None:
    """Realiza a carga das disciplinas usando o dia da carga."""
    wait = WebDriverWait(browser, timeout=30)
    checkbox = wait.until(EC.element_to_be_clickable((By.ID, 'distancia')))
    if checkbox.get_attribute('checked'):
        checkbox.click()

    browser.find_element(By.ID, 'txtAltTurmaDisc').send_keys(
        dia_da_carga_formatado
    )
    browser.find_element(By.ID, 'btDisciplinas').click()

    resultado_popup('Carga das Disciplinas', browser)

    browser.find_element(By.ID, 'txtAltTurmaDisc').clear()


def carga_turmas(browser: WebDriver) -> None:
    """Realiza a carga das turmas usando o dia da carga."""
    wait = WebDriverWait(browser, timeout=30)
    checkbox = wait.until(
        EC.element_to_be_clickable((By.ID, 'turma_distancia'))
    )
    if checkbox.get_attribute('checked'):
        checkbox.click()

    browser.find_element(By.ID, 'txDtTurma').send_keys(dia_da_carga_formatado)
    browser.find_element(By.ID, 'btTurmas').click()

    resultado_popup('Carga das Turmas', browser)

    browser.find_element(By.ID, 'txDtTurma').clear()


def carga_matriculas_presencial(browser: WebDriver) -> None:
    """Realiza a carga das turmas prenciais usando o dia da carga."""
    wait = WebDriverWait(browser, timeout=30)
    checkbox = wait.until(EC.element_to_be_clickable((By.ID, 'mat_distancia')))
    if checkbox.get_attribute('checked'):
        checkbox.click()

    browser.find_element(By.ID, 'txtAltTurma').send_keys(
        dia_da_carga_formatado
    )
    browser.find_element(By.ID, 'btMatriculas').click()

    resultado_popup('Carga das Matrículas - Alteração das Turmas', browser)

    browser.find_element(By.ID, 'txtAltTurma').clear()
    browser.find_element(By.ID, 'txDtMatricula').send_keys(
        dia_da_carga_formatado
    )
    browser.find_element(By.ID, 'btMatriculas').click()

    resultado_popup('Carga das Matrículas - Presenciais', browser)

    browser.find_element(By.ID, 'txtAltTurma').clear()
    browser.find_element(By.ID, 'txDtMatricula').clear()


def carga_matriculas_distancia(browser: WebDriver) -> None:
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


def enviar_email(mensagem: str) -> None:
    sender = os.environ.get('REMETENTE')
    receivers = os.environ.get('DESTINATARIOS')
    password = os.environ.get('SENHA_EMAIL')
    body = f"""{mensagem}"""

    yag = yagmail.SMTP(sender, password)
    yag.send(
        to=receivers.split(','),
        subject=f'Resultado da carga {dia_da_carga_formatado}',
        contents=body,
    )


def fazer_carga():
    usuario = os.environ.get('USUARIO')
    senha = os.environ.get('SENHA')

    browser: WebDriver = None

    while not browser:
        try:
            browser = login(usuario, senha)
        except Exception:
            browser = None

    try:
        carga_disciplinas(browser)
        carga_turmas(browser)
        carga_matriculas_presencial(browser)
        carga_matriculas_distancia(browser)
    except (NoSuchElementException, TimeoutException) as error:
        logger.error(error)

    browser.quit()


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    fazer_carga()
    resultado_log = ler_resultado_log('output.log')
    enviar_email(mensagem=resultado_log)
