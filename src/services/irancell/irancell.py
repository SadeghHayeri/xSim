from src.services.base import BaseService
import requests
from bs4 import BeautifulSoup
from time import time
import pickle
import json
from os import path, makedirs
from src.util.logger import logger
from src.services.irancell.config import BASE_URL, DEFAULT_HEADERS
from src.services.irancell.string_utils import detect_offer_by_name_and_description, detect_offer_by_active_object


class Irancell(BaseService):
    def __init__(self, config):
        auth_info = config['auth']
        self._phone = auth_info['phone'].get()
        self._password = auth_info['password'].get()
        self._session_path = auth_info['session']['path'].get()
        self._session = None

    def authenticate(self):
        self._session = self._get_session()
        self._authenticate()
        self._save_session()

    def _get_session(self):
        session = self._load_session()
        if not session:
            logger.info('create new session')
            session = requests.Session()
        return session

    def _get_csrf(self):
        response = self._session.get(BASE_URL, headers=DEFAULT_HEADERS)
        soup = BeautifulSoup(response.text, features='lxml')
        return soup.find(id='_csrf')['value']

    def _login(self, phone, password, csrf):
        data = {
            'msisdn': phone,
            'password': password,
            '_csrf': csrf,
        }

        url = BASE_URL + '/api/verifyecarepass'
        response = self._session.post(url, headers=DEFAULT_HEADERS, data=data)
        result = json.loads(response.text)

        logger.info(result)

        if result['status'] != 0:
            raise Exception('LOGIN FAILED: ' + result['statusMsg'])

    def _get_session_status(self):
        logger.info('check session')
        url = BASE_URL + '/api/myaccounts_test?_={}'.format(int(time()))
        response = self._session.get(url, headers=DEFAULT_HEADERS)
        is_valid = response.status_code == 200
        logger.info('session is ' + 'VALID' if is_valid else 'EXPIRED')
        return is_valid

    def _authenticate(self):
        if not self._get_session_status():
            logger.info('try authentication')
            csrf = self._get_csrf()
            self._login(self._phone, self._password, csrf)

    def _save_session(self):
        dir_path = path.dirname(self._session_path)

        if not path.exists(dir_path):
            makedirs(dir_path)

        data = {'phone': self._phone, 'session': self._session}
        pickle.dump(data, open(self._session_path, "wb"))

    def _load_session(self):
        if path.exists(self._session_path):
            logger.info('session found')
            data = pickle.load(open(self._session_path, "rb"))

            if data['phone'] == self._phone:
                return data['session']

    def _get_account_info(self):
        url = BASE_URL + '/api/myaccounts_test?_={}'.format(int(time()))
        response = self._session.get(url, headers=DEFAULT_HEADERS)
        return json.loads(response.text)

    def _get_offers(self):
        url = BASE_URL + '/api/getboltonlist'
        data = {'homepage': '0'}
        response = self._session.post(url, data=data, headers=DEFAULT_HEADERS)
        return json.loads(response.text)

    def get_account_balance_and_offers(self):
        account_info = self._get_account_info()
        user_offers = []
        for active_offer in account_info['account']['productPrivateDas']:
            offer = detect_offer_by_active_object(active_offer)
            user_offers.append(offer)
        return int(account_info['account']['balance']), user_offers

    def _get_offer_by_available_offer(self, offer_object):
        offer = detect_offer_by_name_and_description(offer_object['descfa'], offer_object['detaildescfa'])
        offer.set_id(offer_object['id'])
        offer.price = offer_object['price']
        offer.expiry_day = offer_object['expiryday']
        offer.auto_renew = offer_object['autorenew']
        return offer

    def get_offers(self):
        offers_info = self._get_offers()
        offers = filter(lambda x: x['category'] == 'Internet', offers_info['newres'])
        return [self._get_offer_by_available_offer(offer_object) for offer_object in offers]

    def buy_offer(self, id):
        csrf = self._get_csrf()
        data = {
            'id': id,
            '_csrf': csrf,
        }
        url = BASE_URL + '/api/boltonpurchaseoptions'
        response = self._session.post(url, headers=DEFAULT_HEADERS, data=data)
        options = json.loads(response.text)['PaymentOptions']

        logger.info(options)

        data = {
            'id': id,
            'orderreferenceno': options['orderreferenceno'],
            'ipstransactionid': options['ipstransactionid'],
            'userautorenewchoice': 'N',
            'paymentMode': 'MA',
            '_csrf': csrf,
        }
        url = BASE_URL + '/api/capturepaymentbolton'
        response = self._session.post(url, headers=DEFAULT_HEADERS, data=data)
        result = json.loads(response.text)
        logger.info(result)
