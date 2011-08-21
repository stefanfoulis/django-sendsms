# -*- coding: utf-8 -*-

import requests, logging
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_unicode

from .base import BaseSmsBackend

SMSPUBLI_API_URL = 'https://secure.gateway360.com/api/push/'
SMSPUBLI_API_VERSION = 'HTTPV3'
SMSPUBLI_DC = 'SMS'
SMSPUBLI_DR = 0
SMSPUBLI_ROUTE = 2

SMSPUBLI_USERNAME = getattr(settings, 'SMSPUBLI_USERNAME', '')
SMSPUBLI_PASSWORD = getattr(settings, 'SMSPUBLI_PASSWORD', '')
SMSPUBLI_ALLOW_LONG_SMS = getattr(settings, 'SMSPUBLI_ALLOW_LONG_SMS', False)

class SmsBackend(BaseSmsBackend):
    """ 
    SMS Backend smspubli.com provider.
    """

    def _send(self, message):
        params = {
            'V': SMSPUBLI_API_VERSION, 
            'UN': SMSPUBLI_USERNAME, 
            'PWD': SMSPUBLI_PASSWORD,
            'R': SMSPUBLI_ROUTE, 
            'SA': message.from_phone,
            'DA': ','.join(message.to),
            'M': message.body.encode('latin-1'),
            'DC': SMSPUBLI_DC,
            'DR': SMSPUBLI_DR, 
            'UR': message.from_phone
        }
        if SMSPUBLI_ALLOW_LONG_SMS:
            params['LM'] = '1'

        response = requests.post(SMSPUBLI_API_URL, params)
        if response.status_code != 200:
            if  not self.fail_silently:
                raise
            else:
                return False

        response_msg, response_code = response.content.split(':')
        if response_msg == 'OK':
            try:
                if "," in response_code:
                    codes = map(int, response_code.split(","))
                else:
                    codes = [int(response_code)]

                for code in codes:
                    if code == -5:
                        #: TODO send error signal (no $$)
                        pass
                    elif code == -3:
                        #: TODO send error signal (incorrect num)
                        pass

                return True

            except (ValueError, TypeError):
                if not self.fail_silently:
                    raise
                return False
        
        return False

    def send_messages(self, messages):
        counter = 0
        for message in messages:
            res = self._send(message)
            if res:
                counter += 1

        return counter
