# -*- coding: utf-8 -*-
"""
nexmo sms gateway backend. (https://www.nexmo.com/)

~~~~~~~~~~~~~~~~~~~~~~
"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import base64
import requests
import logging

from .base import BaseSmsBackend

logger = logging.getLogger("nexmo")

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

class Error(Exception):
    pass

class ClientError(Error):
    pass

class ServerError(Error):
    pass

class AuthenticationError(ClientError):
    pass

NEXMO_API_URL = 'https://rest.nexmo.com/sms/json'
NEXMO_API_KEY = getattr(settings, 'NEXMO_API_KEY', '')
NEXMO_API_SECRET = getattr(settings, 'NEXMO_PASSWORD', '')

class SmsBackend(BaseSmsBackend):
    
    def get_api_key(self):
        return NEXMO_API_KEY

    def get_api_secret(self):
        return NEXMO_API_SECRET

    def _parse_response(self, response):
        """
        Parse http raw respone into python
        dictionary object.
        
        :param str response: http response
        :returns: response dict
        :rtype: dict
        """

        response_dict = {}
        for line in response.splitlines():
            key, value = response.split("=", 1)
            response_dict[key] = value
        return response_dict


    def parse(self, host, response):

        if response.status_code == 204:
            return None
        elif 200 <= response.status_code < 300:
            content_mime = response.headers.get("content-type").split(";", 1)[0]
            if content_mime == "application/json":
                return response.json()
            else:
                return response.content


        if self.fail_silently:
            logger.warning(
                "Client error: %s %r", response.status_code, response.content
            )
            return False

        if response.status_code == 401:
            raise AuthenticationError
        elif 400 <= response.status_code < 500:
            logger.warning(
                "Client error: %s %r", response.status_code, response.content
            )
            message = "{code} response from {host}".format(
                code=response.status_code, host=host
            )
            try:
                error_data = response.json()
                if (
                    "type" in error_data
                    and "title" in error_data
                    and "detail" in error_data
                ):
                    message = "{title}: {detail} ({type})".format(
                        title=error_data["title"],
                        detail=error_data["detail"],
                        type=error_data["type"],
                    )
            except JSONDecodeError:
                pass
            raise ClientError(message)
        elif 500 <= response.status_code < 600:
            logger.warning(
                "Server error: %s %r", response.status_code, response.content
            )
            message = "{code} response from {host}".format(
                code=response.status_code, host=host
            )
            raise ServerError(message)

    def _send(self, message):
        """
        Private method for send one message.

        :param SmsMessage message: SmsMessage class instance.
        :returns: True if message is sent else False
        :rtype: bool
        """

        params = {
            'from': message.from_phone, 
            'to': ",".join(message.to),
            'text': message.body,
            'api_key': self.get_api_key,
            'api_secret': self.get_api_secret,
        }
 
        uri = "https://{api_uri}".format(api_uri=NEXMO_API_URL)

        logger.debug("POST to %r with body: %r", uri, params)

        return self.parse(uri, requests.post(uri, data=params))

    def send_messages(self, messages):
        """
        Send messages.

        :param list messages: List of SmsMessage instences.
        :returns: number of messages seded succesful.
        :rtype: int
        """
        counter = 0
        for message in messages:
            res = self._send(message)
            if res:
                counter += 1

        return counter
