#-*- coding: utf-8 -*-
from sendsms.utils import load_object
from sendsms import get_connection

def send_sms(body, from_phone, to, flash=False, fail_silently=False,
             auth_user=None, auth_password=None, connection=None):
    """
    Easy wrapper for send a single SMS to a recipient list. 

    :returns: the number of SMSs sent.
    """
    from sendsms.message import SmsMessage
    connection = connection or get_connection(
        username = auth_user, 
        password = auth_password,
        fail_silently = fail_silently
    )
    return SmsMessage(body=body, from_phone=from_phone, to=to, \
        flash=flash, connection=connection).send()


def send_mass_sms(datatuple, fail_silently=False,
             auth_user=None, auth_password=None, connection=None):
    """
    Given a datatuple of (message, from_phone, to, flash), sends each message to each
    recipient list. 
    
    :returns: the number of SMSs sent.
    """

    from sendsms.message import SmsMessage
    connection = connection or get_connection(
        username = auth_user, 
        password = auth_password,
        fail_silently = fail_silently
    )
    messages = [SmsMessage(message=message, from_phone=from_phone, to=to, flash=flash)
                for message, from_phonenumber, to, flash in datatuple]
    connection.send_messages(messages)
