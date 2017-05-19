"""SmsBackend for `thaibulksms.com <http://www.thaibulksms.com/>`_ API.

Configurations
---------------
``SENDSMS_THAIBULKSMS_USERNAME``
  ThaiBulkSMS username (required)

``SENDSMS_THAIBULKSMS_PASSWORD``
  ThaiBulkSMS password (required)

``SENDSMS_THAIBULKSMS_TIMEOUT``
  Connection timeout in seconds (default: 30)

``SENDSMS_THAIBULKSMS_SSL``
  Whether to connect by SSL (default: True)

``SENDSMS_THAIBULKSMS_TEST``
  Whether to connect to test server. Note that enabling this will use a hardcoded test account (default: False)

``SENDSMS_THAIBULKSMS_TYPE``
  Message type (standard or premium, default: standard)
"""

import xml.etree.ElementTree as ET

import requests

from django.conf import settings
from sendsms.backends.base import BaseSmsBackend

class SmsBackend(BaseSmsBackend):
    username = getattr(settings, 'SENDSMS_THAIBULKSMS_USERNAME', '')
    password = getattr(settings, 'SENDSMS_THAIBULKSMS_PASSWORD', '')
    test = getattr(settings, 'SENDSMS_THAIBULKSMS_TEST', False)
    ssl = getattr(settings, 'SENDSMS_THAIBULKSMS_SSL', True)
    sms_type = getattr(settings, 'SENDSMS_THAIBULKSMS_TYPE', 'standard')
    timeout = getattr(settings, 'SENDSMS_THAIBULKSMS_TIMEOUT', 30)

    def __init__(self, *args, **kwargs):
        super(SmsBackend, self).__init__(*args, **kwargs)

        if self.test:
            self.username = 'thaibulksms'
            self.password = 'thisispassword'

        self.endpoint = self.get_endpoint()

    def get_endpoint(self):
        """
        Determine ThaiBulkSMS endpoint from SSL and TEST options
        """
        if self.ssl:
            domain = 'https://secure.thaibulksms.com/'
        else:
            domain = 'http://www.thaibulksms.com/'

        if self.test:
            return domain + 'sms_api_test.php'
        else:
            return domain + 'sms_api.php'

    def send_messages(self, messages):
        """
        Sends one or more SmsMessage objects and returns the number of sms
        messages sent.
        """
        num_sent = 0
        for message in messages:
            to = ','.join(message.to)
            payload = {
                'username': self.username,
                'password': self.password,
                'message': message.body,
                'msisdn': to,
                'sender': message.from_phone,
                'force': self.sms_type,
            }

            response = requests.post(self.endpoint, payload, timeout=self.timeout)

            root = ET.fromstring(response.text)

            if root.find('QUEUE'):
                num_sent += 1
            elif not self.fail_silently:
                error = root.find('Detail').text
                raise SmsException(error)

        return num_sent

class SmsException(Exception):
    """
    Base exception for ThaiBulkSMS
    """
