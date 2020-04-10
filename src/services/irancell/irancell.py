from src.services.base import BaseService
import requests
from bs4 import BeautifulSoup
from time import time
import pickle
import json
from os import path, makedirs
from src.util.logger import logger
from src.services.irancell.config import BASE_URL, DEFAULT_HEADERS
from src.models.offer import Offer
from jdatetime import datetime
import re



class Irancell(BaseService):
    def __init__(self, config):
        auth_info = config['auth']
        self._phone = auth_info['phone'].get()
        self._password = auth_info['password'].get()
        self._session_path = auth_info['session']['path'].get()

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


    def _get_offer_time_limitation(self, name):
        ta_index = name.find('تا')
        if ta_index == -1:
            return None

        lp_index = name.find('(') if name.find('(') >= 0 else 0
        rp_index = name.find(')') if name.find(')') >= 0 else len(name)

        left, right = max(ta_index - 8, lp_index + 1), min(ta_index + 8, rp_index)
        name = name[left:right]

        am_indexes = [{'type': 'AM', 'index': am.start()} for am in re.finditer('صبح', name)]
        pm_indexes = [{'type': 'PM', 'index': pm.start()} for pm in re.finditer('ظهر', name)]

        am_pm_indexes = sorted(am_indexes + pm_indexes, key=lambda name: name['index'])
        assert 0 < len(am_pm_indexes) < 3

        if len(am_pm_indexes) == 1:
            first_am_pm = second_am_pm = am_pm_indexes[0]['type']
        else:
            first_am_pm, second_am_pm = am_pm_indexes[0]['type'], am_pm_indexes[1]['type']

        first_hour, second_hour = list(map(int, re.findall(r'\d+', name)))

        result = [{'hour': first_hour, 'type': first_am_pm}, {'hour': second_hour, 'type': second_am_pm}]
        return result

    def _get_data_size(self, size, unit):
        unit_factor = 1024 ** 3 if unit == ' گیگابایت ' else 1024 ** 2
        return float(size) * unit_factor

    def get_active_offers(self):
        account_info = self._get_account_info()
        # account_info = {'status': 0, 'subscriberType': '1', 'service': '1', 'account': {'productPrivateDas': [{'offerID': '61090', 'offerName': 'یکساله 72 گیگ', 'startDateTime': '1399/01/11 19:07', 'expiryDateTime': '1400/01/10 19:07', 'type': 'D', 'percentage': 6.490071786511521, 'usedValue': '67.32', 'usedunit': ' گیگابایت ', 'offerRemainingValue': '4.67', 'offerRemainingValueUsingNational': '9.35', 'remunitNational': ' گیگابایت ', 'totalValue': '72.00', 'remunit': ' گیگابایت ', 'totunit': ' گیگابایت '}, {'offerID': '71025', 'offerName': 'نامحدود یک ساعته (2 تا 8 صبح)', 'startDateTime': '1399/01/22 03:09', 'expiryDateTime': '1399/01/22 04:12', 'type': 'D', 'percentage': 100, 'usedLocal': '0.00', 'usedGlobal': '0.00', 'usedLocalUnit': ' مگابایت ', 'usedGlobalUnit': ' مگابایت ', 'offerRemainingValue': '20.00', 'offerRemainingValueUsingNational': '40.00', 'remunitNational': ' گیگابایت ', 'totalValue': '20.00', 'remunit': ' گیگابایت ', 'totunit': ' گیگابایت '}], 'data': {'used': '67.33', 'remaining': '24.67', 'percentage': '0.27', 'dataRemUnit': ' گیگابایت ', 'dataUsedUnit': ' گیگابایت ', 'dataTotalUnit': ' گیگابایت ', 'peakRemaining': '4.67', 'offpeakRemaining': '20.00', 'peakRemainingUnit': ' گیگابایت ', 'offpeakRemainingUnit': ' گیگابایت '}, 'voice': {'used': '0.00', 'remaining': '0.00', 'totalVoice': '0.00', 'percentage': 'NaN', 'voiceUnit': 'دقیقه'}, 'sms': {'used': '0.00', 'remaining': '0.00', 'totalSMS': '0.00', 'percentage': 'NaN', 'smsUnit': 'پیامک'}, 'nonProductPrivateDas': [], 'balance': '173094', 'tariffPlanName': 'طرح کنترل مصرف آزاد', 'tariffPlanCode': 'DBU', 'activationCode': '1391/01/12'}}

        return [
            Offer(
                active_offer['offerID'],
                active_offer['offerName'],
                datetime.strptime(active_offer['startDateTime'], '%Y/%m/%d %H:%M'),
                datetime.strptime(active_offer['expiryDateTime'], '%Y/%m/%d %H:%M'),
                self._get_data_size(active_offer['totalValue'], active_offer['totunit']),
                self._get_data_size(active_offer['offerRemainingValue'], active_offer['remunit']),
                self._get_offer_time_limitation(active_offer['offerName']),
            ) for active_offer in account_info['account']['productPrivateDas']
        ]


