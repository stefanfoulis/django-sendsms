"""
Configuration example
---------------------

settings.py:

    SMS_CSI_BACKEND = 'sendsms.backends.smscsi.Csi'
    SMS_CSI_USERNAME = 'xxxxxxxxxxxxx'
    SMS_CSI_PASSWORD = 'xxxxxxxxxxxxx'
    SMS_CSI_CODICE_PROGETTO = xxxxxx
    SMS_CSI_PRIORITA = xxxxx
    SMS_CSI_URL = 'xxxxxxxxxxxxxxxxx'

"""
import logging
import requests
import tempfile
import xml.etree.ElementTree as ET

from django.conf import settings

from sendsms.backends.base import BaseSmsBackend

logger = logging.getLogger(__name__)

SMS_CSI_USERNAME = getattr(settings, 'SMS_CSI_USERNAME', '')
SMS_CSI_PASSWORD = getattr(settings, 'SMS_CSI_PASSWORD', '')
SMS_CSI_URL = getattr(settings, 'SMS_CSI_URL', '')
SMS_CSI_CODICE_PROGETTO = getattr(settings, 'SMS_CSI_CODICE_PROGETTO', '')
SMS_CSI_PRIORITA = getattr(settings, 'SMS_CSI_PRIORITA', '')


class Csi(BaseSmsBackend):
    
    def send_messages(self, messages):
        sent = 0
        if not messages:
            return sent
        for message in messages:
            try:
                self._send(message)
            except Exception as e:
                if not self.fail_silently:
                    raise e
                else:
                    logger.exception(str(e))
            else:
                sent += 1
        return sent
    
    def _send(self, message):
        if not self.is_valid(message.body):
            return
        recipients = ','.join(message.to).replace("+", "")
        note = '-,' * len(message.to)
        # remove last comma
        note = note[:len(note) - 1]
        xml_data = (
            '<RICHIESTA_SMS>'
            f'<USERNAME>{SMS_CSI_USERNAME}</USERNAME>'
            f'<PASSWORD>{SMS_CSI_PASSWORD}</PASSWORD>'
            f'<CODICE_PROGETTO>{SMS_CSI_CODICE_PROGETTO}</CODICE_PROGETTO>'
            '<SMS>'
            f'<TELEFONO>{recipients}</TELEFONO>'
            f'<TESTO>{message.body}</TESTO>'
            f'<PRIORITA>{SMS_CSI_PRIORITA}</PRIORITA>'
            f'<NOTE>{note}</NOTE>'
            '</SMS>'
            '</RICHIESTA_SMS>'
        )
        logger.debug(f'Invio di sms: {message.body}')
        xml = ET.ElementTree(ET.fromstring(xml_data))
        with tempfile.TemporaryFile() as xml_file:
            xml.write(xml_file)
            xml_file.seek(0)
            response = requests.post(
                SMS_CSI_URL,
                {'xmlSms': xml_file}
            )
        response_data = ET.fromstring(response.content)
        if response.status_code != 200 or response_data[0].text == 'ERRORE':
            error_message = (
                f'Invio sms non riuscito, stato: {response.status_code}\n'
                f'Contenuto della risposta: {response_data[1].text}'
            )
            self._raise_error(error_message)
        logger.debug('Il messaggio è stato inviato con successo.')
    
    def is_valid(self, message):
        length = len(message)
        vowels = 'àáèéìíòóùúÀÁÈÉÌÍÒÓÙÚ'
        for vowel in vowels:
            if vowel in message:
                length += 1
        if length > 160:
            error_message = 'La lunghezza del messaggio ha superato il lunghezza massima di 160.'
            self._raise_error(error_message)
            return False
        return True
    
    def _raise_error(self, error_message):
        if not self.fail_silently:
            raise Exception(error_message)
        else:
            logger.exception(error_message)
