#-*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

try:
    # Django versions >= 1.9
    from django.utils.module_loading import import_module
except ImportError:
    # Django versions < 1.9
    from django.utils.importlib import import_module
from sendsms.utils import load_object


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
                for message, from_phone, to, flash in datatuple]
    connection.send_messages(messages)


def get_connection(path=None, fail_silently=False, **kwargs):
    """
    Load an sms backend and return an instance of it.

    :param string path: backend python path. Default: sendsms.backends.console.SmsBackend
    :param bool fail_silently: Flag to not throw exceptions on error. Default: False
    :returns: backend class instance.
    :rtype: :py:class:`~sendsms.backends.base.BaseSmsBackend` subclass
    """

    path = path or getattr(settings, 'SENDSMS_BACKEND', 'sendsms.backends.locmem.SmsBackend')
    try:
        mod_name, klass_name = path.rsplit('.', 1)
        mod = import_module(mod_name)
    except AttributeError as e:
        raise ImproperlyConfigured(u'Error importing sms backend module %s: "%s"' % (mod_name, e))

    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" class' % (mod_name, klass_name))

    return klass(fail_silently=fail_silently, **kwargs)
