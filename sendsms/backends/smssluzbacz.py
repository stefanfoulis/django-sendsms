#    The New BSD License
#
#    Copyright (c) 2011-2012, CodeScale s.r.o.
#    All rights reserved.
#
#    Redistribution and use in source and binary forms, with or without modification,
#    are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#    * Neither the name of CodeScale s.r.o. nor the names of its contributors
#    may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
#    INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#    WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
#    USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging
import unicodedata

from smssluzbacz_api.lite import SmsGateApi
from django.conf import settings

from sendsms.backends.base import BaseSmsBackend


log = logging.getLogger(__name__)


class SmsBackend(BaseSmsBackend):
    """SmsBackend for sms.sluzba.cz API.

    settings.py configuration constants:
      SMS_SLUZBA_API_LOGIN - sms.sluzba.cz login
      SMS_SLUZBA_API_PASSWORD - sms.sluzba.cz password
      SMS_SLUZBA_API_TIMEOUT - connection timeout to sms.sluzba.cz in seconds
      SMS_SLUZBA_API_USE_SSL - whether to use ssl via http or not
      SMS_SLUZBA_API_USE_POST - whether to use GET or POST http method

    """

    def __init__(self, fail_silently=False, **kwargs):
        super(SmsBackend, self).__init__(fail_silently=fail_silently, **kwargs)
        self.open()

    def __del__(self):
        self.close()

    def open(self):
        """Initializes sms.sluzba.cz API library."""
        self.client = SmsGateApi(getattr(settings, 'SMS_SLUZBA_API_LOGIN', ''),
                                 getattr(settings, 'SMS_SLUZBA_API_PASSWORD', ''),
                                 getattr(settings, 'SMS_SLUZBA_API_TIMEOUT', 2),
                                 getattr(settings, 'SMS_SLUZBA_API_USE_SSL', True))

    def close(self):
        """Cleaning up the reference for sms.sluzba.cz API library."""
        self.client = None

    def send_messages(self, messages):
        """Sending SMS messages via sms.sluzba.cz API.

        Note:
          This method returns number of actually sent sms messages
          not number of SmsMessage instances processed.

        :param messages: list of sms messages
        :type messages: list of sendsms.message.SmsMessage instances
        :returns: number of sent sms messages
        :rtype: int

        """
        count = 0
        for message in messages:
            message_body = unicodedata.normalize('NFKD', unicode(message.body)).encode('ascii', 'ignore')
            for tel_number in message.to:
                try:
                    self.client.send(tel_number, message_body, getattr(settings, 'SMS_SLUZBA_API_USE_POST', True))
                except Exception:
                    if self.fail_silently:
                        log.exception('Error while sending sms via sms.sluzba.cz backend API.')
                    else:
                        raise
                else:
                    count += 1

        return count