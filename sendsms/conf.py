#-*- coding: utf-8 -*-
from django.conf import settings

def get(key, default):
    return getattr(settings, key, default)

BACKEND = get('SENDSMS_BACKEND', 'sendsms.backends.console.SmsBackend')
DEFAULT_FROM_PHONE = get('SENDSMS_DEFAULT_FROM_PHONE', '')
