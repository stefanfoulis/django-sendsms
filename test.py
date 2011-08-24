# -*- coding: utf-8 -*-

import unittest
from django.conf import settings

import sendsms

if not settings.configured:
    settings.configure(
        SMS_BACKEND = 'sendsms.backends.locmem.SmsBackend',
        ESENDEX_USERNAME = 'niwibe',
        ESENDEX_PASSWORD = '123123',
        ESENDEX_ACCOUNT = '123123',
        ESENDEX_SANDBOX = True,
    )


class TestApi(unittest.TestCase):
    def test_send_simple_sms(self):
        from sendsms.message import SmsMessage
        obj = SmsMessage(body="test", from_phone='111111111', to=['222222222'])
        obj.send()

        self.assertEqual(len(sendsms.outbox), 1)

    def test_send_esendex_sandbox(self):
        from sendsms.message import SmsMessage
        from sendsms.api import get_connection

        connection = get_connection('sendsms.backends.esendex.SmsBackend')
        obj = SmsMessage(body="test", from_phone='111111111', to=['222222222'], connection=connection)
        res = obj.send()
        self.assertEqual(res, 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)


