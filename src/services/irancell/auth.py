import requests
from bs4 import BeautifulSoup
from src.config import config
from time import time
import pickle
import json
from os import path, makedirs
from src.util.logger import logger

irancell_config = config['irancell']
auth_info = irancell_config['auth']

PHONE = auth_info['phone'].get()
PASSWORD = auth_info['password'].get()
SESSION_PATH = auth_info['session']['path'].get()

DEFAULT_HEADERS = {
    'Host': 'my.irancell.ir',
    'User-Agent': '/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://my.irancell.ir',
    'Connection': 'close',
}


def get_csrf(session):
    response = session.get('https://my.irancell.ir', headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(response.text, features='lxml')
    return soup.find(id='_csrf')['value']


def login(session, phone, password, csrf):
    data = {
        'msisdn': phone,
        'password': password,
        '_csrf': csrf,
    }

    response = session.post('https://my.irancell.ir/api/verifyecarepass', headers=DEFAULT_HEADERS, data=data)
    result = json.loads(response.text)

    if result['status'] != 0:
        raise Exception('LOGIN FAILED: ' + result['statusMsg'])


def is_valid_session(session):
    response = session.get('https://my.irancell.ir/api/myaccounts_test?_=' + str(int(time())), headers=DEFAULT_HEADERS)
    return response.status_code == 200


def get_account_info(session):
    response = session.get('https://my.irancell.ir/api/myaccounts_test?_=' + str(int(time())), headers=DEFAULT_HEADERS)
    return json.loads(response.text)


def authenticate(session):
    csrf = get_csrf(session)
    login(session, PHONE, PASSWORD, csrf)


def save_session(session):
    dir_path = path.dirname(SESSION_PATH)

    if not path.exists(dir_path):
        makedirs(dir_path)

    data = {
        'phone': PHONE,
        'session': session,
    }
    pickle.dump(data, open(SESSION_PATH, "wb"))


def load_session():
    if path.exists(SESSION_PATH):
        logger.info('session found')
        data = pickle.load(open(SESSION_PATH, "rb"))

        if data['phone'] == PHONE:
            return data['session']


def get_session():
    session = load_session()
    if not session:
        logger.info('create new session')
        session = requests.Session()

    if not is_valid_session(session):
        logger.info('try authenticate')
        authenticate(session)
        logger.info('save session')

    save_session(session)

    return session


session = get_session()
logger.info(session)
