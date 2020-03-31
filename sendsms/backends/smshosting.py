"""
smshosting backend. (https://www.smshosting.it)

Configuration example.
----------------------

settings.py::

    SENDSMS_BACKEND = 'sendsms.backends.smshosting.SmsHostingBackend'
    SMSHOSTING_AUTH_KEY = 'XXXXXXXXXXXXXXXXXXXXX'
    SMSHOSTING_AUTH_SECRET = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    SMSHOSTING_SANDBOX = False  # if omitted, defaults to settings.DEBUG
"""

import logging

from django.conf import settings

import requests
from requests.auth import HTTPBasicAuth

from sendsms.backends.base import BaseSmsBackend

logger = logging.getLogger(__name__)

SMSHOSTING_AUTH_KEY = getattr(settings, "SMSHOSTING_AUTH_KEY", "")
SMSHOSTING_AUTH_SECRET = getattr(settings, "SMSHOSTING_AUTH_SECRET", "")
SMSHOSTING_SEND_URL = getattr(
    settings, "SMSHOSTING_SEND_URL", "https://api.smshosting.it/rest/api/sms/send"
)
SMSHOSTING_SANDBOX = getattr(settings, "SMSHOSTING_SANDBOX", settings.DEBUG)


class SmsHostingBackend(BaseSmsBackend):
    def send_messages(self, messages):
        sent = 0
        if not messages:
            return sent
        for message in messages:
            try:
                return self._send(message)
            except Exception as e:
                if not self.fail_silently:
                    raise e
                else:
                    logger.exception("SMS sending failed")
            else:
                sent += 1
        return sent

    def _send(self, message):
        recipients = ",".join(message.to)
        data = {
            "from": message.from_phone.replace("+", ""),
            "to": recipients.replace("+", ""),
            "text": message.body,
            "sandbox": "true" if SMSHOSTING_SANDBOX else "false",
        }
        logger.debug("Sending SMS, params: {}".format(data))
        response = requests.post(
            SMSHOSTING_SEND_URL,
            data=data,
            auth=HTTPBasicAuth(SMSHOSTING_AUTH_KEY, SMSHOSTING_AUTH_SECRET),
        )
        if response.status_code != 200:
            raise Exception(
                "SMS sending failed, status: {}, "
                "response content: {}".format(response.status_code, response.content)
            )
        response_data = response.json()
        logger.info(
            "Sent SMS to {}\n"
            "transactionId: {}\n"
            "smsInserted: {}\n"
            "smsNotInserted: {}\n"
            "sms: {}".format(
                recipients,
                response_data["transactionId"],
                response_data["smsInserted"],
                response_data["smsNotInserted"],
                response_data["sms"],
            )
        )
        return response
