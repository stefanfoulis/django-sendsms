# -*- coding: utf-8 -*-

sms_post_send = django.dispatch.Signal(providing_args=['from_phone','to','body'])
