""" celery based backend

This backend will send your messages asynchronously with celery.

Before using this backend, make sure that celery is installed and
configured.

This backend is based on the rq backend.

Usage
-----

In settings.py


    SENDSMS_BACKEND = 'sendsms.backends.celery.SmsBackend'
    CELERY_SENDSMS_BACKEND = 'actual.backend.to.use.SmsBackend'


"""
from __future__ import absolute_import

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from celery import shared_task

from sendsms.api import get_connection
from sendsms.backends.base import BaseSmsBackend

CELERY_SENDSMS_BACKEND = getattr(settings, "CELERY_SENDSMS_BACKEND", None)

if not CELERY_SENDSMS_BACKEND:
    raise ImproperlyConfigured("Set CELERY_SENDSMS_BACKEND")


@shared_task
def send_messages(messages):
    connection = get_connection(CELERY_SENDSMS_BACKEND)
    connection.send_messages(messages)


class SmsBackend(BaseSmsBackend):
    def send_messages(self, messages):
        send_messages.delay(messages)
