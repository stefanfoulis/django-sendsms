#-*- coding: utf-8 -*-

import requests

from django.conf import settings
from sendsms.backends.base import BaseSmsBackend


BULKSMS_API_URL = 'https://bulksms.vsms.net/eapi/submission/send_sms/2/2.0'
BULKSMS_USERNAME = getattr(settings, 'SENDSMS_BULKSMS_USERNAME', '')
BULKSMS_PASSWORD = getattr(settings, 'SENDSMS_BULKSMS_PASSWORD', '')
BULKSMS_ENABLE_UNICODE = getattr(
    settings, 'SENDSMS_BULKSMS_ENABLE_UNICODE', False)


class SmsBackend(BaseSmsBackend):
    """
    Bulksms gateway backend. (http://www.bulksms.com)
    Based on http://developer.bulksms.com/eapi/code-samples/python/send_sms/
    Docs in http://developer.bulksms.com/eapi/submission/send_sms/

    Settings::

        SENDSMS_BACKEND = 'sendsms.backends.bulksms.SmsBackend'
        SENDSMS_BULKSMS_USERNAME = 'xxx'
        SENDSMS_BULKSMS_PASSWORD = 'xxx'

    Usage::
        from sendsms import api
        api.send_sms(
            body='I can haz txt', from_phone='+41791111111', to=['+41791234567']
        )

    """

    def string_to_hex(self, body):
        # Based on http://developer.bulksms.com/eapi/code-samples/java/unicode/
        # and http://developer.bulksms.com/eapi/submission/faq/
        body = body.decode('utf-8')
        chars = list(body)
        output = ''

        for i in range(len(chars)):
            _next = hex(ord(body[i])).replace('0x', '')
            # Unfortunately, hex doesn't pad with zeroes, so we have to.
            for j in range(4 - len(_next)):
                output += '0'
            output += _next

        return output

    def send_messages(self, messages):
        for message in messages:
            to = ', '.join(message.to)
            payload = {
                'username': BULKSMS_USERNAME,
                'password': BULKSMS_PASSWORD,
                'message': message.body,
                'msisdn': to  # without 00 or +
            }
            if BULKSMS_ENABLE_UNICODE:
                payload['dca'] = '16bit'
                payload['message'] = self.string_to_hex(message.body)

            response = requests.post(BULKSMS_API_URL, payload)

            # response.status_code will always be 200 even with an error.
            result = response.text.split('|')
            status_code = result[0]
            status_msg = result[1]
            if status_code != '0':
                if not self.fail_silently:
                    raise Exception(
                        "Error: " + status_code + ": " + status_msg)
                else:
                    return False
            else:
                print("Message sent: batch ID " + result[2])

        return True


