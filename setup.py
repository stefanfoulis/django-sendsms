from setuptools import setup, find_packages

version = __import__('sendsms').__version__

setup(
    name="django-sendsms",
    version=version,
    url='http://github.com/stefanfoulis/django-sendsms',
    license='BSD',
    platforms=['OS Independent'],
    description="A simple API to send SMS messages.",
    long_description=open('README.rst').read(),
    author='Stefan Foulis',
    author_email='stefan@foulis.ch',
    maintainer='Stefan Foulis',
    maintainer_email='stefan@foulis.ch',
    packages=find_packages(),
    include_package_data=True,
    extras_require={
        'celery': ['celery'],
        'esendex': ['requests'],
        'twilio': ['twilio'],
        'smssluzbacz': ['smssluzbacz-api'],
        'rq': ['django_rq'],
    },
    test_suite="test",
    tests_require=[
        'mock',
        'django',
        'requests',
        'django_rq',
        'twilio',
        'celery',
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
