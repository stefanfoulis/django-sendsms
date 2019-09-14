==============
django-sendsms
==============

.. image:: https://coveralls.io/repos/github/stefanfoulis/django-sendsms/badge.svg?branch=master
    :target: https://coveralls.io/github/stefanfoulis/django-sendsms?branch=master

.. image:: https://travis-ci.org/stefanfoulis/django-sendsms.svg?branch=master
    :target: https://travis-ci.org/stefanfoulis/django-sendsms

.. image:: https://badge.fury.io/py/django-sendsms.svg
    :target: https://badge.fury.io/py/django-sendsms

A simple api to send SMS messages with django. The api is structured the same way as Django's own email api.

Installation
============

::

    pip install django-sendsms

Configure the ``SENDSMS_BACKEND`` (defaults to ``'sendsms.backends.console.SmsBackend'``)::

    SENDSMS_BACKEND = 'myapp.mysmsbackend.SmsBackend'


Basic usage
===========

Sending SMSs is like sending emails::

    from sendsms import api
    api.send_sms(body='I can haz txt', from_phone='+41791111111', to=['+41791234567'])

You can also make instances of ``SmsMessage``::

    from sendsms.message import SmsMessage
    message = SmsMessage(body='lolcats make me hungry', from_phone='+41791111111', to=['+41791234567'])
    message.send()


Custom backends
===============

Creating custom ``SmsBackend`` s::

    from sendsms.backends.base import BaseSmsBackend
    import some.sms.delivery.api

    class AwesomeSmsBackend(BaseSmsBackend):
        def send_messages(self, messages):
            for message in messages:
                for to in message.to:
                    try:
                        some.sms.delivery.api.send(
                            message=message.body,
                            from_phone=message.from_phone,
                            to_phone=to,
                            flashing=message.flash
                        )
                    except:
                        if not self.fail_silently:
                            raise

Then all you need to do is reference your backend in the ``SENDSMS_BACKEND`` setting.


Running tests
=============

::

    python setup.py test

Or better, install and run "tox".


Contributing
============


Pull requests are very welcome. Please make sure code is formatted using black and isort.


