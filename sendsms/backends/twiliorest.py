#-*- coding: utf-8 -*-

"""
this backend requires the twilio python library: http://pypi.python.org/pypi/twilio/
"""
import twilio
if twilio.__version__ > 5:
    TWILIO_5 = False
    from twilio.rest import Client as TwilioRestClient
else:
    TWILIO_5 = True
    from twilio.rest import TwilioRestClient

from django.conf import settings
from sendsms.backends.base import BaseSmsBackend

TWILIO_ACCOUNT_SID = getattr(settings, 'SENDSMS_TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = getattr(settings, 'SENDSMS_TWILIO_AUTH_TOKEN', '')


class SmsBackend(BaseSmsBackend):
    def send_messages(self, messages):
        client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        for message in messages:
            for to in message.to:
                try:
                    if TWILIO_5:
                        client.sms.messages.create(
                            body=message.body,
                            to=to,
                            from_=message.from_phone,
                        )
                    else:
                        client.messages.create(
                            to=to,
                            from_=message.from_phone,
                            body=message.body
                        )
                except:
                    if not self.fail_silently:
                        raise
