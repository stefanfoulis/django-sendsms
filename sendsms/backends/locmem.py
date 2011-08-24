#-*- coding: utf-8 -*-
"""
Backend for test environment.
"""

import sendsms
from sendsms.backends.base import BaseSmsBackend

class SmsBackend(BaseSmsBackend):
    """
    A sms backend for use during test sessions.

    The test connection stores messages in a dummy outbox,
    rather than sending them out on the wire.
    The dummy outbox is accessible through the outbox instance attribute.
    """
    def __init__(self, *args, **kwargs):
        super(SmsBackend, self).__init__(*args, **kwargs)
        if not hasattr(sendsms, 'outbox'):
            sendsms.outbox = []

    def send_messages(self, messages):
        """Redirect messages to the dummy outbox"""
        sendsms.outbox.extend(messages)
        return len(messages)
