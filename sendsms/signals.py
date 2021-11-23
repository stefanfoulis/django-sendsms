# -*- coding: utf-8 -*-
from django.dispatch import Signal

sms_post_send = Signal()  # providing_args=["from_phone", "to", "body"]
