#-*- coding: utf-8 -*-
from sendsms import get_connection


class SmsMessage(object):
    """
    A sms message
    """
    def __init__(self, message, from_phone=None, to=None, flash=False, connection=None):
        """
        Initialize a single SMS message (which can be sent to multiple recipients
        """
        if to:
            assert not isinstance(to, basetring), '"to" argument must be a list or tuple'
            self.to = list(to)
        else:
            self.to = []
        self.from_phone = from_phone or settings.SENDSMS_DEFAULT_FROM_PHONE
        self.message = message
        self.flash = flash
        self.connection = connection

    def get_connection(self, fail_silently=False):
        if not self.connection:
            self.connection = get_connection(fail_silently=fail_silently)
        return self.connection

    def send(self, fail_silently=False):
        """
        Sends the sms message
        """
        if not self.to:
            # Don't bother creating the connection if there's nobody to send to
            return 0
        return self.get_connection(fail_silently).send_messages([self])
