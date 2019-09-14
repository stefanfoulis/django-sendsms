# -*- coding: utf-8 -*-
import django.dispatch

sms_post_send = django.dispatch.Signal(providing_args=["from_phone", "to", "body"])
