# -*- coding: utf-8 -*-

try:
    from unittest import mock
except:
    import mock

try:
    from importlib import reload
except:
    pass

import unittest

from django.conf import settings
from django.test import SimpleTestCase

import sendsms

if not settings.configured:
    settings.configure(
        SENDSMS_BACKEND="sendsms.backends.locmem.SmsBackend",
        ESENDEX_USERNAME="niwibe",
        ESENDEX_PASSWORD="123123",
        ESENDEX_ACCOUNT="123123",
        ESENDEX_SANDBOX=True,
        RQ_QUEUES={"default": {"URL": "redis://localhost", "DEFAULT_TIMEOUT": 500}},
        RQ_SENDSMS_BACKEND="sendsms.backends.locmem.SmsBackend",
        CELERY_SENDSMS_BACKEND="sendsms.backends.locmem.SmsBackend",
    )


class TestApi(unittest.TestCase):
    def test_send_simple_sms(self):
        from sendsms.message import SmsMessage

        obj = SmsMessage(body="test", from_phone="111111111", to=["222222222"])
        obj.send()

        self.assertEqual(len(sendsms.outbox), 1)

    def test_send_esendex_sandbox(self):
        from sendsms.message import SmsMessage
        from sendsms.api import get_connection

        connection = get_connection("sendsms.backends.esendex.SmsBackend")
        obj = SmsMessage(
            body="test", from_phone="111111111", to=["222222222"], connection=connection
        )
        res = obj.send()
        self.assertEqual(res, 1)


class RQBackendTest(SimpleTestCase):
    @mock.patch("sendsms.backends.rq.send_messages")
    def test_should_queue_sms(self, send_messages_mock):
        from sendsms.message import SmsMessage

        with self.settings(SENDSMS_BACKEND="sendsms.backends.rq.SmsBackend"):
            message = SmsMessage(
                body="Hello!", from_phone="29290", to=["+639123456789"]
            )
            message.send()

        send_messages_mock.delay.assert_called_with([message])

    @mock.patch("sendsms.backends.twiliorest.SmsBackend")
    @mock.patch("sendsms.backends.locmem.SmsBackend")
    def test_send_message_should_use_configured_backend(
        self, LocmemBackend, TwilioBackend
    ):
        from sendsms.message import SmsMessage

        with self.settings(SENDSMS_BACKEND="sendsms.backends.rq.SmsBackend"):
            with self.settings(
                RQ_SENDSMS_BACKEND="sendsms.backends.twiliorest.SmsBackend"
            ):  # noqa
                from sendsms.backends import rq

                backend = TwilioBackend()
                message = SmsMessage(
                    body="Hello!", from_phone="29290", to=["+639123456789"]
                )
                rq.send_messages([message])
                backend.send_messages.assert_called_once_with([message])

            with self.settings(
                RQ_SENDSMS_BACKEND="sendsms.backends.locmem.SmsBackend"
            ):  # noqa
                reload(rq)

                backend = LocmemBackend()
                message = SmsMessage(
                    body="Hello!", from_phone="29290", to=["+639123456789"]
                )
                rq.send_messages([message])
                backend.send_messages.assert_called_once_with([message])


class CeleryBackendTest(SimpleTestCase):
    @mock.patch("sendsms.backends.celery.send_messages")
    def test_should_queue_sms(self, send_messages_mock):
        from sendsms.message import SmsMessage

        with self.settings(SENDSMS_BACKEND="sendsms.backends.celery.SmsBackend"):
            message = SmsMessage(
                body="Hello!", from_phone="29290", to=["+639123456789"]
            )
            message.send()

        send_messages_mock.delay.assert_called_with([message])

    @mock.patch("sendsms.backends.twiliorest.SmsBackend")
    @mock.patch("sendsms.backends.locmem.SmsBackend")
    def test_send_message_should_use_configured_backend(
        self, LocmemBackend, TwilioBackend
    ):
        from sendsms.message import SmsMessage

        with self.settings(SENDSMS_BACKEND="sendsms.backends.celery.SmsBackend"):
            with self.settings(
                CELERY_SENDSMS_BACKEND="sendsms.backends.twiliorest.SmsBackend"
            ):  # noqa
                from sendsms.backends import celery

                backend = TwilioBackend()
                message = SmsMessage(
                    body="Hello!", from_phone="29290", to=["+639123456789"]
                )
                celery.send_messages([message])
                backend.send_messages.assert_called_once_with([message])

            with self.settings(
                CELERY_SENDSMS_BACKEND="sendsms.backends.locmem.SmsBackend"
            ):  # noqa
                reload(celery)

                backend = LocmemBackend()
                message = SmsMessage(
                    body="Hello!", from_phone="29290", to=["+639123456789"]
                )
                celery.send_messages([message])
                backend.send_messages.assert_called_once_with([message])


class OvhBackendTest(SimpleTestCase):
    @mock.patch(
        "sendsms.backends.ovhsms.OvhSmsBackend._call_url", return_value={"result": "42"}
    )
    def test_should_call_proper_url(self, _call_url_mock):
        from sendsms.message import SmsMessage

        with self.settings(
            SENDSMS_BACKEND="sendsms.backends.ovhsms.OvhSmsBackend",
            OVH_API_URL="http://fakeurl/",
            OVH_API_ACCOUNT="myaccount",
            OVH_API_LOGIN="mylogin",
            OVH_API_PASSWORD="mypwd",
            OVH_API_FROM="mysender",
            OVH_API_NO_STOP=False,
        ):

            message = SmsMessage(
                body="Hello!",
                from_phone="29290",  # overrides OVH_API_FROM
                to=["+639123456789"],
            )
            res = message.send()
            self.assertEqual(res, [{"result": "42"}])

        expected = (
            "http://fakeurl/?account=myaccount&class=1&contentType=text%2Fjson&from=29290&login=mylogin&"
            "message=Hello%21&noStop=0&password=mypwd&smsCoding=2&to=%2B639123456789",
        )

        self.assertEqual(_call_url_mock.call_args, (expected,))

        with self.settings(
            SENDSMS_BACKEND="sendsms.backends.ovhsms.OvhSmsBackend",
            OVH_API_ACCOUNT="myaccount",
            OVH_API_LOGIN="mylogin",
            OVH_API_PASSWORD="mypwd",
            OVH_API_FROM="mysender",
        ):

            message = SmsMessage(
                body="Wêlcome à vous\nHenrï & Jack!\r\n",
                from_phone="thierry",  # overrides OVH_API_FROM
                to=["0699"],
            )
            res = message.send()
            self.assertEqual(res, [{"result": "42"}])

            expected = (
                "https://www.ovh.com/cgi-bin/sms/http2sms.cgi?account=myaccount&class=1&contentType=text%2Fjson&"
                "from=thierry&login=mylogin&message=W%C3%AAlcome+%C3%A0+vous%0DHenr%C3%AF+%26+Jack%21%0D&"
                "noStop=1&password=mypwd&smsCoding=2&to=0699",
            )
            self.assertEqual(_call_url_mock.call_args, (expected,))

    def test_should_properly_handle_errors(self):
        with self.settings(
            SENDSMS_BACKEND="sendsms.backends.ovhsms.OvhSmsBackend",
            OVH_API_ACCOUNT="myaccount",
            OVH_API_LOGIN="mylogin",
            OVH_API_PASSWORD="mypwd",
            OVH_API_FROM="mysender",
        ):

            from sendsms.api import send_sms

            with self.assertRaisesRegex(RuntimeError, "Invalid smsAccount"):
                send_sms(body="I can hàz txt", from_phone=None, to=["+33632020000"])

            res = send_sms(
                body="I can hàz txt",
                from_phone=None,
                to=["+33632020000"],
                fail_silently=True,
            )
            self.assertEqual(res, [])


if __name__ == "__main__":
    unittest.main(verbosity=2, buffer=True)
