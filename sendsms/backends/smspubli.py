# -*- coding: utf-8 -*-

"""
SmsPubli sms gateway backend. (http://www.smspubli.com)

Configuration example.
----------------------

Modify your settings.py::

    SMSPUBLI_USERNAME = 'yourusername'
    SMSPUBLI_PASSWORD = 'mysecretpassword'
    SMSPUBLI_ALLOW_LONG_SMS = True # or False
    INSTALLED_APPS += ['sendsms']


Usage::

    from sendsms.message import SmsMessage
    message = SmsMessage(
        body = 'my 160 chars sms',
        from_phone = '111111111',
        to = ['222222222']
    )
    message.send()
"""

from django.conf import settings

import requests

from .base import BaseSmsBackend

SMSPUBLI_API_URL = "https://secure.gateway360.com/api/push/"
SMSPUBLI_API_VERSION = "HTTPV3"
SMSPUBLI_DC = "SMS"
SMSPUBLI_DR = 0
SMSPUBLI_ROUTE = 2

SMSPUBLI_USERNAME = getattr(settings, "SMSPUBLI_USERNAME", "")
SMSPUBLI_PASSWORD = getattr(settings, "SMSPUBLI_PASSWORD", "")
SMSPUBLI_ALLOW_LONG_SMS = getattr(settings, "SMSPUBLI_ALLOW_LONG_SMS", False)


class SmsBackend(BaseSmsBackend):
    """
    SMS Backend smspubli.com provider.

    The methods "get_xxxxxx" serve to facilitate the inheritance. Thus if a private
    project in the access data are dynamic, and are stored in the database. A child
    class overrides the method "get_xxxx" to return data stored in the database.
    """

    def get_username(self):
        return SMSPUBLI_USERNAME

    def get_password(self):
        return SMSPUBLI_PASSWORD

    def _send(self, message):
        """
        Private method for send one message.

        :param SmsMessage message: SmsMessage class instance.
        :returns: True if message is sended else False
        :rtype: bool
        """

        params = {
            "V": SMSPUBLI_API_VERSION,
            "UN": SMSPUBLI_USERNAME,
            "PWD": SMSPUBLI_PASSWORD,
            "R": SMSPUBLI_ROUTE,
            "SA": message.from_phone,
            "DA": ",".join(message.to),
            "M": message.body.encode("latin-1"),
            "DC": SMSPUBLI_DC,
            "DR": SMSPUBLI_DR,
            "UR": message.from_phone,
        }
        if SMSPUBLI_ALLOW_LONG_SMS:
            params["LM"] = "1"

        response = requests.post(SMSPUBLI_API_URL, params)
        if response.status_code != 200:
            if not self.fail_silently:
                raise
            else:
                return False

        response_msg, response_code = response.content.split(":")
        if response_msg == "OK":
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
        """
        Send messages.

        :param list messages: List of SmsMessage instences.
        :returns: number of messages seded succesful.
        :rtype: int
        """

        counter = 0
        for message in messages:
            res = self._send(message)
            if res:
                counter += 1

        return counter
