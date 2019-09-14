try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode  # Python2
import json
import logging

from django.conf import settings

import requests

from sendsms.backends.base import BaseSmsBackend

logger = logging.getLogger(__name__)


class OvhSmsBackend(BaseSmsBackend):
    @staticmethod
    def _call_url(url):
        res = requests.get(url)
        res.raise_for_status()
        data = json.loads(res.text)
        if data.get("status") == 100:
            logger.info("OVH SMS successfully sent: %s", repr(data))
        else:
            raise RuntimeError(
                "OVH SMS sending returned error structure: %s" % repr(data)
            )
        return data

    @classmethod
    def _send_via_ovh(
        cls,
        message,
        to_phone,  # must be "00336xxxx"-like international format
        from_phone=None,
        flashing=False,
        tag=None,  # string of max 20 characters
        deferred=None,
    ):  # eg. format "125025112017" for sending on 28/11/2017 at 12h50

        # late lookup, else tests won't work...
        OVH_API_URL = getattr(
            settings, "OVH_API_URL", "https://www.ovh.com/cgi-bin/sms/http2sms.cgi"
        )
        OVH_API_ACCOUNT = getattr(settings, "OVH_API_ACCOUNT", "")
        OVH_API_LOGIN = getattr(settings, "OVH_API_LOGIN", "")
        OVH_API_PASSWORD = getattr(settings, "OVH_API_PASSWORD", "")
        OVH_API_FROM = getattr(settings, "OVH_API_FROM", "")
        OVH_API_NO_STOP = getattr(settings, "OVH_API_NO_STOP", True)
        OVH_API_SMS_CODING = 2  # UTF8-encoded characters, but max 70 characters per SMS

        # for some reason OVH wants "%0d" (CR character) for newlines
        message = message.replace("\r\n", "\r")
        message = message.replace("\n", "\r")

        params = {
            "account": OVH_API_ACCOUNT,
            "login": OVH_API_LOGIN,
            "password": OVH_API_PASSWORD,
            "from": from_phone or OVH_API_FROM,
            "class": ("0" if flashing else "1"),  # flash SMS appears directly on screen
            "smsCoding": OVH_API_SMS_CODING,
            "contentType": "text/json",
            "noStop": ("1" if OVH_API_NO_STOP else "0"),  # we don't send commercial SMS
            "message": message,
            "to": to_phone,
        }

        if tag:
            params["tag"] = tag
        if deferred:
            params["deferred"] = deferred

        query_string = urlencode(sorted(params.items()))
        full_url = "{}?{}".format(OVH_API_URL, query_string)

        return cls._call_url(full_url)

    def send_messages(self, messages):
        results = []
        for message in messages:
            for (
                to_phone
            ) in message.to:  # For now we separate recipients in different SMS
                try:
                    res = self._send_via_ovh(
                        message=message.body,
                        to_phone=to_phone,
                        from_phone=message.from_phone,
                        flashing=message.flash,
                    )
                    results.append(res)
                except:
                    logger.error("OVH SMS sending failed", exc_info=True)
                    if not self.fail_silently:
                        raise
        return results
