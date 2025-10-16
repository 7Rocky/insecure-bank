import time

from selenium.webdriver import Chrome, ChromeOptions, ChromeService
from selenium.webdriver.common.by import By


ADMIN_USERNAME = 'admin'
VICTIM_USERNAME = 'victim'


def get_password(username: str) -> str:
    with open(f'{username}_password.txt') as f:
        return f.read()


def get_client():
    chrome_options = ChromeOptions()

    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-background-networking')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-sync')
    chrome_options.add_argument('--disable-translate')
    chrome_options.add_argument('--metrics-recording-only')
    chrome_options.add_argument('--mute-audio')
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--safebrowsing-disable-auto-update')
    chrome_options.add_argument('--js-flags=--noexpose_wasm,--jitless')

    client = Chrome(options=chrome_options, service=ChromeService(executable_path='/usr/bin/chromedriver'))
    client.set_page_load_timeout(5)
    client.set_script_timeout(5)

    return client


def visit():
    client = get_client()

    client.get('http://127.0.0.1:5000/')
    time.sleep(2)

    login = client.find_element(By.NAME, 'login')
    login.click()
    time.sleep(2)

    username = client.find_element(By.ID, 'username')
    password = client.find_element(By.ID, 'password')
    submit = client.find_element(By.ID, 'submit')
    username.send_keys(VICTIM_USERNAME)
    password.send_keys(get_password(VICTIM_USERNAME))
    submit.click()
    time.sleep(2)

    # Solo quiero ver mi perfil y comprobar mis transferencias...

    client.quit()


def verify():
    client = get_client()

    client.get('http://127.0.0.1:5000/')
    time.sleep(2)

    login = client.find_element(By.NAME, 'login')
    login.click()
    time.sleep(2)

    username = client.find_element(By.ID, 'username')
    password = client.find_element(By.ID, 'password')
    submit = client.find_element(By.ID, 'submit')
    username.send_keys(ADMIN_USERNAME)
    password.send_keys(get_password(ADMIN_USERNAME))
    submit.click()
    time.sleep(2)

    # Quiero que mi cookie de sesión sea segura frente a ataques de XSS...
    client.add_cookie({'name': 'session', 'value': client.get_cookie('session').get('value'), 'httpOnly': True})

    admin_verify = client.find_element(By.NAME, 'admin_verify')
    admin_verify.click()
    time.sleep(2)

    # No quiero verificar a nadie, así que rechazo a todos...
    for reject in client.find_elements(By.NAME, 'reject'):
        reject.click()
        time.sleep(0.5)

    time.sleep(2)
    client.quit()


def report(url: str):
    client = get_client()
    
    client.get('http://127.0.0.1:5000/')
    time.sleep(2)

    login = client.find_element(By.NAME, 'login')
    login.click()
    time.sleep(2)

    username = client.find_element(By.ID, 'username')
    password = client.find_element(By.ID, 'password')
    submit = client.find_element(By.ID, 'submit')
    username.send_keys(ADMIN_USERNAME)
    password.send_keys(get_password(ADMIN_USERNAME))
    submit.click()
    time.sleep(2)

    # Quiero que mi cookie de sesión sea segura frente a ataques de XSS...
    client.add_cookie({'name': 'session', 'value': client.get_cookie('session').get('value'), 'httpOnly': True})

    # No sé qué quieres que haga con esta URL de búsqueda...
    client.get(url)
    time.sleep(2)

    # Yo no veo nada...
    # Me vuelvo a mi perfil...

    login = client.find_element(By.NAME, 'login')
    login.click()
    time.sleep(2)

    username = client.find_element(By.ID, 'username')
    password = client.find_element(By.ID, 'password')
    submit = client.find_element(By.ID, 'submit')
    username.send_keys(ADMIN_USERNAME)
    password.send_keys(get_password(ADMIN_USERNAME))
    submit.click()
    time.sleep(2)

    client.quit()
