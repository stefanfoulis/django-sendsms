# -*- coding: utf-8 -*-


class BaseSmsBackend(object):
    """
    Base class for sms backend implementations.

    Subclasses must at least overwrite send_messages()
    """

    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently

    def open(self):
        """
        Open a network connection.

        This method can be overwritten by backend implementations to open a network connection.
        It's up to the backend implementation to track the status of
        a network connection if it's needed by the backend.
        This method can be called by applications to force a single
        network connection to be used when sending multiple SMSs.

        The default implementation does nothing.
        """
        pass

    def close(self):
        """Close a network connection"""
        pass

    def send_messages(self, messages):
        """
        Sends one or more SmsMessage objects and returns the number of messages sent
        """
        raise NotImplementedError
