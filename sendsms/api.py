#-*- coding: utf-8 -*-
from sendsms.utils import load_object
from sendsms import conf


def get_connection(backend=None, fail_silently=False, **kwargs):
    """
    Load an SMS backend and return an instance of it.

    If backend is None (default) settings.SENDSMS_BACKEND is used.

    Bot fail_silently and other keyword arguments are used in the constructor
    of the backend.
    """
    path = backend or conf.BACKEND
    klass = load_object(path)
    return klass(fail_silently=fail_silently, **kwargs)

def send_sms(body, from_phone, to, flash=False, fail_silently=False,
             auth_user=None, auth_password=None, connection=None):
    """
    Easy wrapper for send a single SMS to a recipient list. Returns the number of SMSs sent.
    """
    from sendsms.message import SmsMessage
    connection = connection or get_connection(
        username=auth_user, password=auth_password,
        fail_silently=fail_silently)
    return SmsMessage(body=body, from_phone=from_phone, to=to, flash=flash, connection=connection).send()


def send_mass_sms(datatuple, fail_silently=False,
             auth_user=None, auth_password=None, connection=None):
    """
    Given a datatuple of (message, from_phone, to, flash), sends each message to each
    recipient list. Returns the number of SMSs sent.
    """
    from sendsms.message import SmsMessage
    connection = connection or get_connection(
        username=auth_user, password=auth_password,
        fail_silently=fail_silently)
    messages = [SmsMessage(message=message, from_phone=from_phone, to=to, flash=flash)
                for message, from_phonenumber, to, flash in datatuple]
    connection.send_messages(messages)
