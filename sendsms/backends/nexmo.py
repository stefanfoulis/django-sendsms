# -*- coding: utf-8 -*-
"""
nexmo sms gateway backend. (https://www.nexmo.com/)

Author: Alican Toprak (a.toprak@northernbitcoin.com)

~~~~~~~~~~~~~~~~~~~~~~
"""

import logging

from django.conf import settings

import requests

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


NEXMO_API_URL = "https://rest.nexmo.com/sms/json"
NEXMO_API_KEY = getattr(settings, "SENDSMS_ACCOUNT_SID", "")
NEXMO_API_SECRET = getattr(settings, "SENDSMS_AUTH_TOKEN", "")


nexmo_error_codes = {
    1: [
        "Throttled",
        "You have exceeded the submission capacity allowed on this account. Please wait and retry.",
    ],
    2: [
        "Missing params",
        "Your request is incomplete and missing some mandatory parameters.",
    ],
    3: ["Invalid params", "The value of one or more parameters is invalid."],
    4: [
        "Invalid credentials",
        "The api_key / api_secret you supplied is either invalid or disabled.",
    ],
    5: [
        "Internal error",
        "There was an error processing your request in the Platform.",
    ],
    6: [
        "Invalid message",
        "The Platform was unable to process your request. For example, due to an unrecognised prefix for the phone number.",
    ],
    7: [
        "Number barred",
        "The number you are trying to submit to is blacklisted and may not receive messages.",
    ],
    8: [
        "Partner account barred",
        "The api_key you supplied is for an account that has been barred from submitting messages.",
    ],
    9: [
        "Partner quota exceeded",
        "Your pre-paid account does not have sufficient credit to process this message.",
    ],
    11: [
        "Account not enabled for REST",
        "This account is not provisioned for REST submission, you should use SMPP instead.",
    ],
    12: [
        "Message too long",
        "The length of udh and body was greater than 140 octets for a binary type SMS request.",
    ],
    13: [
        "Communication Failed",
        "Message was not submitted because there was a communication failure.",
    ],
    14: [
        "Invalid Signature",
        "Message was not submitted due to a verification failure in the submitted signature.",
    ],
    15: [
        "Illegal Sender Address - rejected",
        "Due to local regulations, the SenderID you set in from in the request was not accepted. Please check the Global messaging section.",
    ],
    16: ["Invalid TTL", "The value of ttl in your request was invalid."],
    19: [
        "Facility not allowed",
        "Your request makes use of a facility that is not enabled on your account.",
    ],
    20: [
        "Invalid Message class",
        "The value of message-class in your request was out of range. See https://en.wikipedia.org/wiki/Data_Coding_Scheme.",
    ],
    23: [
        "Bad callback :: Missing Protocol",
        "You did not include https in the URL you set in callback.",
    ],
    29: [
        "Non White-listed Destination",
        "The phone number you set in to is not in your pre-approved destination list. To send messages to this phone number, add it using Dashboard.",
    ],
    34: [
        "Invalid or Missing Msisdn Param",
        "The phone number you supplied in the to parameter of your request was either missing or invalid.",
    ],
}


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
        if not response.status_code == 200:
            if self.fail_silently:
                logger.warning("Error: %s %r", response.status_code, response.content)
                return False
            raise Error("Error: %s %r", response.status_code, response.content)

        status_code = int(response.json().get("messages")[0].get("status"))

        if status_code == 0:
            return True, response

        error_type = nexmo_error_codes.get(status_code)

        if self.fail_silently:
            logger.warning("Error: %s %r", response.status_code, response.content)
            return False, requests

        raise ClientError(
            "Error Code {status_code}: {text}:  {meaning}".format(
                status_code=status_code, text=error_type[0], meaning=error_type[1]
            )
        )

    def _send(self, message):
        """
        A helper method that does the actual sending

        :param SmsMessage message: SmsMessage class instance.
        :returns: True if message is sent else False
        :rtype: bool
        """

        params = {
            "from": message.from_phone,
            "to": ",".join(message.to),
            "text": message.body,
            "api_key": self.get_api_key(),
            "api_secret": self.get_api_secret(),
        }

        print(params)

        logger.debug("POST to %r with body: %r", NEXMO_API_URL, params)

        return self.parse(NEXMO_API_URL, requests.post(NEXMO_API_URL, data=params))

    def send_messages(self, messages):
        """
        Send messages.

        :param list messages: List of SmsMessage instances.
        :returns: number of messages sended successful.
        :rtype: int
        """
        counter = 0
        for message in messages:
            res, _ = self._send(message)
            if res:
                counter += 1

        return counter
