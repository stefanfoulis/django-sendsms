# -*- coding: utf-8 -*-

"""
this backend requires the boto3 (amazon aws's python sdk): https://aws.amazon.com/sdk-for-python/
"""
import boto3
from django.conf import settings

from sendsms.backends.base import BaseSmsBackend

AMAZON_AWS_ACCESS_KEY_ID = getattr(settings, "AMAZON_AWS_ACCESS_KEY_ID", "")
AMAZON_AWS_SECRET_ACCESS_KEY_ID = getattr(settings, "AMAZON_AWS_SECRET_ACCESS_KEY_ID", "")
AMAZON_AWS_REGION_NAME = getattr(settings, "AMAZON_AWS_REGION_NAME", "us-east-1")


class SmsBackend(BaseSmsBackend):
    def send_messages(self, messages):
        client = boto3.client(
            "sns",
            aws_access_key_id=AMAZON_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AMAZON_AWS_SECRET_ACCESS_KEY_ID,
            region_name=AMAZON_AWS_REGION_NAME
        )
        for message in messages:
            for to in message.to:
                try:
                    client.publish(PhoneNumber=to, Message=message.body)
                except:
                    if not self.fail_silently:
                        raise
