from django.conf import settings
import boto.ses
import sendgrid
import requests
from django.core.mail import EmailMultiAlternatives
from django_ses_gateway.sending_mail import sending_mail


def Memail(mto, mfrom, msubject, mbody, email_template_name, context):
    if settings.MAIL_SENDER == 'AMAZON':
        sending_mail(msubject, email_template_name, context, mfrom, mto)
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
        text_content = msubject
        msg = EmailMultiAlternatives(msubject, mbody, mfrom, mto)
        msg.attach_alternative(mbody, "text/html")
        msg.send()
