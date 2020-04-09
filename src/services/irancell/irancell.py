from src.services.base import BaseService
import requests
from bs4 import BeautifulSoup
from time import time
import pickle
import json
from os import path, makedirs
from src.util.logger import logger
from src.services.irancell.config import DEFAULT_HEADERS


class Irancell(BaseService):
    def __init__(self, config):
        auth_info = config['auth']
        self.phone = auth_info['phone'].get()
        self.password = auth_info['password'].get()
        self.session_path = auth_info['session']['path'].get()

    def _get_csrf(self, session):
        response = session.get('https://my.irancell.ir', headers=DEFAULT_HEADERS)
        soup = BeautifulSoup(response.text, features='lxml')
        return soup.find(id='_csrf')['value']

    def _login(self, session, phone, password, csrf):
        data = {
            'msisdn': phone,
            'password': password,
            '_csrf': csrf,
        }

        response = session.post('https://my.irancell.ir/api/verifyecarepass', headers=DEFAULT_HEADERS, data=data)
        result = json.loads(response.text)

        if result['status'] != 0:
            raise Exception('LOGIN FAILED: ' + result['statusMsg'])

    def _is_valid_session(self, session):
        response = session.get('https://my.irancell.ir/api/myaccounts_test?_=' + str(int(time())),
                               headers=DEFAULT_HEADERS)
        return response.status_code == 200

    def _authenticate(self, session):
        csrf = self._get_csrf(session)
        self._login(session, self.phone, self.password, csrf)

    def _save_session(self, session):
        dir_path = path.dirname(self.session_path)

        if not path.exists(dir_path):
            makedirs(dir_path)

        data = {
            'phone': self.phone,
            'session': session,
        }
        pickle.dump(data, open(self.session_path, "wb"))

    def _load_session(self):
        if path.exists(self.session_path):
            logger.info('session found')
            data = pickle.load(open(self.session_path, "rb"))

            if data['phone'] == self.phone:
                return data['session']

    def _get_session(self, ):
        session = self._load_session()
        if not session:
            logger.info('create new session')
            session = requests.Session()

        if not self._is_valid_session(session):
            logger.info('try authenticate')
            self._authenticate(session)
            logger.info('save session')

        self._save_session(session)

        return session

    def _get_account_info(self, session):
        response = session.get('https://my.irancell.ir/api/myaccounts_test?_=' + str(int(time())),
                               headers=DEFAULT_HEADERS)
        return json.loads(response.text)
