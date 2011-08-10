#-*- coding: utf-8 -*-
"""
Dummy sms backend that does nothing.
"""

from sendsms.backends.base import BaseSmsBackend

class SmsBackend(BaseSmsBackend):
    def send_messages(self, messages):
        return len(messages)
