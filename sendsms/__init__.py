#-*- coding: utf-8 -*-
__version_info__ = {
    'major': 0,
    'minor': 1,
    'micro': 1,
    'releaselevel': 'final',
    'serial': 1
}

def get_version(short=False):
    assert __version_info__['releaselevel'] in ('alpha', 'beta', 'final')
    vers = ["%(major)i.%(minor)i" % __version_info__, ]
    if __version_info__['micro']:
        vers.append(".%(micro)i" % __version_info__)
    if __version_info__['releaselevel'] != 'final' and not short:
        vers.append('%s%i' % (__version_info__['releaselevel'][0], __version_info__['serial']))
    return ''.join(vers)

__version__ = get_version()

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


def get_connection(path=None, fail_silently=False, **kwargs):
    """
    Load an sms backend and return an instance of it.

    :param string path: backend python path. Default: sendsms.backends.console.SmsBackend
    :param bool fail_silently: Flag to not throw exceptions on error. Default: False
    :returns: backend class instance.
    :rtype: :py:class:`~sendsms.backends.base.BaseSmsBackend` subclass
    """

    path = path or getattr(settings, 'SMS_BACKEND', 'sendsms.backends.locmem.SmsBackend')
    try:
        mod_name, klass_name = path.rsplit('.', 1)
        mod = import_module(mod_name)
    except AttributeError as e:
        raise ImproperlyConfigured(u'Error importing sms backend module %s: "%s"' % (mod_name, e))

    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" class' % (mod_name, klass_name))

    return klass(fail_silently=fail_silently, **kwargs)
