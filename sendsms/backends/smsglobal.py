"""SMS Global sms backend class."""
from django.conf import settings
import urllib2
import urllib
import re
import logging
import math
from .base import BaseSmsBackend
from decimal import Decimal

logger = logging.getLogger(__name__)

SMSGLOBAL_USERNAME = getattr(settings, 'SMSGLOBAL_USERNAME', '')
SMSGLOBAL_PASSWORD = getattr(settings, 'SMSGLOBAL_PASSWORD', '')
SMSGLOBAL_CHECK_BALANCE_COUNTRY = getattr(settings, 'SMSGLOBAL_CHECK_BALANCE_COUNTRY', False)
SMSGLOBAL_API_URL_SENDSMS = 'https://www.smsglobal.com.au/http-api.php'
SMSGLOBAL_API_URL_CHECKBALANCE = 'https://www.smsglobal.com/credit-api.php'

class SmsBackend(BaseSmsBackend):
    """
    A wrapper that manages the SMS Global network connection.
    
    Sending and parsing functionality borrowed from http://namingcrisis.net/code
    """

    def get_username(self):
        return SMSGLOBAL_USERNAME
    
    def get_password(self):
        return SMSGLOBAL_PASSWORD

    def get_balance(self):
        """
        Get balance with provider.
        """
        if not SMSGLOBAL_CHECK_BALANCE_COUNTRY:
            raise Exception('SMSGLOBAL_CHECK_BALANCE_COUNTRY setting must be set to check balance.')
        
        params = {
          'user' : self.get_username(),
          'password' : self.get_password(),
          'country' : SMSGLOBAL_CHECK_BALANCE_COUNTRY,
        }
        
        req = urllib2.Request(SMSGLOBAL_API_URL_CHECKBALANCE, urllib.urlencode(params))
        response = urllib2.urlopen(req).read()

        # CREDITS:8658.44;COUNTRY:AU;SMS:3764.54;
        if response.startswith('ERROR'):
            raise Exception('Error retrieving balance: %s' % response.replace('ERROR:', ''))
        
        return dict([(p.split(':')[0].lower(), p.split(':')[1]) for p in response.split(';') if len(p) > 0])

    def send_messages(self, sms_messages):
        """
        Sends one or more SmsMessage objects and returns the number of sms
        messages sent.
        """
        if not sms_messages:
            return
        
        num_sent = 0
        for message in sms_messages:
            if self._send(message):
                num_sent += 1
        return num_sent

    def _send(self, message):
        """A helper method that does the actual sending."""
        charset='UTF-8'
        params = {
          'action' : 'sendsms',
          'user' : self.get_username(),
          'password' : self.get_password(),
          'from' : message.from_phone,
          'to' : ",".join(message.to),
          'text' : message.body,
          'clientcharset' : charset,
          'detectcharset' : 1,
          'maxsplit': int(math.ceil(len(message.body) / 160))
        }
        
        req = urllib2.Request(SMSGLOBAL_API_URL_SENDSMS, urllib.urlencode(params))
        result_page = urllib2.urlopen(req).read()
        results = self._parse_response(result_page)
        
        if results is None:
            if not self.fail_silently:
                raise Exception("Error determining response: [" + result_page + "]")
            return False
        
        code, sendqmsgid, msgid = results
        
        if code != '0':
            if not self.fail_silently:
                raise Exception("Error sending sms: [%s], extracted results(code, sendqmsgid, msgid): [%s]" % (result_page, results))
            return False
        else:
            logger.info('SENT to: %s; sender: %s; code: %s; sendqmsgid: %s; msgid: %s; message: %s' % (
                message.to,
                message.from_phone,
                code, 
                sendqmsgid, 
                msgid,
                message.body
            ))
            return True
    
    def _parse_response(self, result_page):
        """
        Takes a result page of sending the sms, returns an extracted tuple:
            ('numeric_err_code', '<sent_queued_message_id>', '<smsglobalmsgid>')
        Returns None if unable to extract info from result_page, it should be
        safe to assume that it was either a failed result or worse, the interface
        contract has changed.
        """
        # Sample result_page, single line -> "OK: 0; Sent queued message ID: 2063619577732703 SMSGlobalMsgID:6171799108850954"
        resultline = result_page.splitlines()[0] # get result line
        if resultline.startswith('ERROR:'):
            raise Exception(resultline.replace('ERROR: ', ''))
        patt = re.compile(r'^.+?:\s*(.+?)\s*;\s*Sent queued message ID:\s*(.+?)\s*SMSGlobalMsgID:(.+?)$', re.IGNORECASE)
        m = patt.match(resultline)
        if m:
            return (m.group(1), m.group(2), m.group(3)) 
        return None       