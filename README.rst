django-simple-forum:
=====================================
.. image:: https://readthedocs.org/projects/django-simple-forum/badge/?version=latest
   :target: http://django-simple-forum.readthedocs.io/en/latest/
   :alt: Documentation Status

.. image:: https://travis-ci.org/MicroPyramid/django-simple-forum.svg?branch=master
   :target: https://travis-ci.org/MicroPyramid/django-simple-forum

.. image:: https://img.shields.io/pypi/dm/django-simple-forum.svg
    :target: https://pypi.python.org/pypi/django-simple-forum
    :alt: Downloads

.. image:: https://img.shields.io/pypi/v/django-simple-forum.svg
    :target: https://pypi.python.org/pypi/django-simple-forum
    :alt: Latest Release

.. image:: https://coveralls.io/repos/github/MicroPyramid/django-simple-forum/badge.svg
   :target: https://coveralls.io/github/MicroPyramid/django-simple-forum

.. image:: https://landscape.io/github/MicroPyramid/django-simple-forum/master/landscape.svg?style=flat
   :target: https://landscape.io/github/MicroPyramid/django-simple-forum/master
   :alt: Code Health

.. image:: https://img.shields.io/github/license/micropyramid/django-simple-forum.svg
    :target: https://pypi.python.org/pypi/django-simple-forum/
    :alt: Latest Release


Introduction:
=============

`django simple forum`_ is a discussion board where people with similar interests can create and discuss various topics. You can also mention any particpant those are involved in the repsective topic in the comment. You can also receive email notifications when there is an update in the topic, when you follow the topic.


Source Code is available in `Micropyramid Repository`_.

Modules used:

    * Python  >= 2.6 (or Python 3.4)
    * Django  = 1.9.6
    * JQuery  >= 1.7
    * Microurl >=3.6.1
    * Boto == 2.40.0
    * Sendgrid == 2.2.1
    * django-ses-gateway

Installation Procedure
======================

1. Install django-simple-forum using the following command::

    pip install django-simple-forum

            (or)

    git clone git://github.com/micropyramid/django-simple-forum.git

    cd django-simple-forum

    python setup.py install

2. Add app name in settings.py::

    INSTALLED_APPS = [
       '..................',
       'compressor',
       'django_simple_forum',
       '..................'
    ]

3. After installing/cloning, add the following details in settings file to send emails notifications::

    # AWS details

    AWS_ACCESS_KEY_ID = "Your AWS Access Key"

    AWS_SECRET_ACCESS_KEY = "Your AWS Secret Key"

                or

    SG_USER = "Your Sendgrid Username"
    SG_PWD = "Your Sendgrid Password"

4. Use virtualenv to install requirements::

    pip install -r requirements.txt


You can view the complete documentation here. `Documentation`_

You can try it by hosting on your own or deploy to Heroku with a button click.

Deploy To Heroku:

.. image:: https://www.herokucdn.com/deploy/button.svg
   :target: https://heroku.com/deploy?template=https://github.com/MicroPyramid/django-simple-forum/


We are always looking to help you customize the whole or part of the code as you like.

Visit our Django Page `Here`_

We welcome your feedback and support, raise `github ticket`_ if you want to report a bug. Need new features? `Contact us here`_

    or

mailto:: "hello@micropyramid.com"

.. _contact us here: https://micropyramid.com/contact-us/
.. _Documentation: http://django-simple-forum.readthedocs.io/en/latest/
.. _github ticket: https://github.com/MicroPyramid/django-simple-forum/issues
.. _django simple forum: https://micropyramid.com/oss/
.. _Micropyramid Repository: https://github.com/MicroPyramid/django-simple-forum.git
.. _Here: https://micropyramid.com/django-development-services/
