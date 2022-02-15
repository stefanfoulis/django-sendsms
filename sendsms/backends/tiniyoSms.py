# -*- coding: utf-8 -*-

from django.conf import settings

import requests

from sendsms.backends.base import BaseSmsBackend

TINIYO_API_URL = "https://api.tiniyo.com/v1/Account/SENDSMS_TINIYO_TOKEN_ID/Message"
TINIYO_TOKEN_ID = getattr(settings, "SENDSMS_TINIYO_TOKEN_ID", "")
TINIYO_TOKEN_SECRET = getattr(settings, "SENDSMS_TINIYO_TOKEN_SECRET", "")


class SmsBackend(BaseSmsBackend):
    """
    Tiniyo gateway backend. (https://tiniyo.com)
    Docs in https://tiniyo.com/docs/#/quickstart
    Settings::
        SENDSMS_BACKEND = 'sendsms.backends.tiniyo.SmsBackend'
        SENDSMS_TINIYO_TOKEN_ID = 'xxx'
        SENDSMS_TINIYO_TOKEN_SECRET = 'xxx'
    Usage::
        from sendsms import api
        api.send_sms(
            body='This is first sms to tiniyo', from_phone='TINIYO', to=['+13525051111']
        )
    """

    def send_messages(self, messages):
        payload = []
        for m in messages:
            entry = {"src": m.from_phone, "dst": m.to, "text": m.body}
            payload.append(entry)
        api_url = TINIYO_API_URL.replace("SENDSMS_TINIYO_TOKEN_ID", TINIYO_TOKEN_ID)
        response = requests.post(
            api_url, json=payload, auth=(TINIYO_TOKEN_ID, TINIYO_TOKEN_SECRET)
        )

        if response.status_code != 200:
            if self.fail_silently:
                return False
            raise Exception(
                "Error: %d: %s"
                % (response.status_code, response.content.decode("utf-8"))
            )

        return True
