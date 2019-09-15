# -*- coding: utf-8 -*-

from django.conf import settings

import requests

from sendsms.backends.base import BaseSmsBackend

BULKSMS_API_URL = "https://api.bulksms.com/v1/messages"
BULKSMS_TOKEN_ID = getattr(settings, "SENDSMS_BULKSMS_TOKEN_ID", "")
BULKSMS_TOKEN_SECRET = getattr(settings, "SENDSMS_BULKSMS_TOKEN_SECRET", "")
BULKSMS_ENABLE_UNICODE = getattr(settings, "SENDSMS_BULKSMS_ENABLE_UNICODE", True)


class SmsBackend(BaseSmsBackend):
    """
    BulkSMS gateway backend. (http://www.bulksms.com)
    Docs in https://www.bulksms.com/developer/json/v1/

    Settings::

        SENDSMS_BACKEND = 'sendsms.backends.bulksms.SmsBackend'
        SENDSMS_BULKSMS_TOKEN_ID = 'xxx'
        SENDSMS_BULKSMS_TOKEN_SECRET = 'xxx'
        BULKSMS_ENABLE_UNICODE = True (default)

    Usage::
        from sendsms import api
        api.send_sms(
            body='I can haz txt', from_phone='+41791111111', to=['+41791234567']
        )

    """

    def send_messages(self, messages):
        payload = []
        for m in messages:
            entry = {"from": m.from_phone, "to": m.to, "body": m.body}
            if BULKSMS_ENABLE_UNICODE:
                entry["encoding"] = "UNICODE"
            payload.append(entry)

        response = requests.post(
            BULKSMS_API_URL, json=payload, auth=(BULKSMS_TOKEN_ID, BULKSMS_TOKEN_SECRET)
        )

        if response.status_code != 201:
            if self.fail_silently:
                return False
            raise Exception(
                "Error: %d: %s"
                % (response.status_code, response.content.decode("utf-8"))
            )

        return True
