""" python-rq based backend

This backend will send your messages asynchronously with python-rq.

Before using this backend, make sure that django-rq is installed and
configured.

Usage
-----

In settings.py


    SENDSMS_BACKEND = 'sendsms.backends.rq.SmsBackend'
    RQ_SENDSMS_BACKEND = 'actual.backend.to.use.SmsBackend'


"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django_rq import job

from sendsms.api import get_connection
from sendsms.backends.base import BaseSmsBackend

RQ_SENDSMS_BACKEND = getattr(settings, "RQ_SENDSMS_BACKEND", None)

if not RQ_SENDSMS_BACKEND:
    raise ImproperlyConfigured("Set RQ_SENDSMS_BACKEND")


@job
def send_messages(messages):
    connection = get_connection(RQ_SENDSMS_BACKEND)
    connection.send_messages(messages)


class SmsBackend(BaseSmsBackend):
    def send_messages(self, messages):
        send_messages.delay(messages)
