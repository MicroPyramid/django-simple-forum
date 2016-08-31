from django.conf import settings
import boto.ses
import sendgrid
import requests
from django.core.mail import EmailMultiAlternatives


def Memail(mto, mfrom, msubject, mbody):
    print (settings.MAIL_SENDER)
    if settings.MAIL_SENDER == 'AMAZON':
        # conn=SESConnection(settings.AM_ACCESS_KEY, settings.AM_PASS_KEY)
        conn = boto.ses.connect_to_region(
            'eu-west-1',
            aws_access_key_id=settings.AM_ACCESS_KEY,
            aws_secret_access_key=settings.AM_PASS_KEY
        )
        conn.send_email(mfrom, msubject, mbody, mto, format='html')

    elif settings.MAIL_SENDER == 'MAILGUN':
        requests.post(
            settings.MGUN_API_URL,
            auth=('api', settings.MGUN_API_KEY),
            data={
                'from': mfrom,
                'to': mto,
                'subject': msubject,
                'html': mbody
            })
    elif settings.MAIL_SENDER == 'SENDGRID':
        sg = sendgrid.SendGridClient(settings.SG_USER, settings.SG_PWD)
        sending_msg = sendgrid.Mail()
        sending_msg.set_subject(msubject)
        sending_msg.set_html(mbody)
        sending_msg.set_text(msubject)
        sending_msg.set_from(mfrom)
        sending_msg.add_to(mto)
        reposne = sg.send(sending_msg)
        print (reposne)
    else:
        print (mto)
        text_content = msubject
        msg = EmailMultiAlternatives(msubject, mbody, mfrom, mto)
        msg.attach_alternative(mbody, "text/html")
        msg.send()
