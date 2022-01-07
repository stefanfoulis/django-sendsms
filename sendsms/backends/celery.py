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
    # optional, celery task parameters
    CELERY_SENDSMS_TASK_CONFIG = {}

"""
from __future__ import absolute_import

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.six import string_types

from celery import shared_task

from sendsms.api import get_connection
from sendsms.backends.base import BaseSmsBackend

CELERY_SENDSMS_BACKEND = getattr(settings, "CELERY_SENDSMS_BACKEND", None)

if not CELERY_SENDSMS_BACKEND:
    raise ImproperlyConfigured("Set CELERY_SENDSMS_BACKEND")

TASK_CONFIG = {"name": "sendsms_send_messages", "ignore_result": True}

CELERY_SENDSMS_TASK_CONFIG = getattr(settings, "CELERY_SENDSMS_TASK_CONFIG", None)

if CELERY_SENDSMS_TASK_CONFIG:
    TASK_CONFIG.update(settings.CELERY_SENDSMS_TASK_CONFIG)

# import base if string to allow a base celery task
if "base" in TASK_CONFIG and isinstance(TASK_CONFIG["base"], string_types):
    from django.utils.module_loading import import_string

    TASK_CONFIG["base"] = import_string(TASK_CONFIG["base"])


@shared_task(**TASK_CONFIG)
def send_messages(messages):
    connection = get_connection(CELERY_SENDSMS_BACKEND)
    connection.send_messages(messages)


class SmsBackend(BaseSmsBackend):
    def send_messages(self, messages):
        send_messages.delay(messages)
