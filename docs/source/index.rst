django-simple-forum's documentation:
=====================================

Introduction:
=============

django-simple-forum is a discussion board where people with similar interests can create and discuss various topics. You can also mention any particpant those are involved in the repsective topic in the comment. You can also receive email notifications when there is an update in the topic, when you follow the topic.


Source Code is available in Micropyramid Repository(https://github.com/MicroPyramid/django-simple-forum.git).

Modules used:

    * Python  >= 2.6 (or Python 3.4)
    * Django  = 1.9.6
    * JQuery  >= 1.7
    * Django-compressor == 2.0
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


Frontend Features:
===================

    * Social logins(facebook, gplus logins) for one click registration in forum.
    * Create topics for a category.
    * User can follow the topic, receive email notifications if you have enabled email notification settings in the profile.
    * User can vote to a topic, like a topic for displaying their interest.
    * When you commenting to a topic, you can refer any other member involved in the comment.
    * You can also send email notifications from the aws, sendgrid, mailgun email application by providing the application credentials.

Dashboard Features:
===================

    * You can see all categories, topics, tags, badges lists in the admin dashboard, cand do the crud operations.
    * You can activate/deactiavte the topic to publish/hide it in forum.
    * We can give badges to the user, if user is an active user and to encourage the user activities.


We are always looking to help you customize the whole or part of the code as you like.


We welcome your feedback and support, raise github ticket if you want to report a bug. Need new features? `Contact us here`_

.. _contact us here: https://micropyramid.com/contact-us/

    or

mailto:: "hello@micropyramid.com"