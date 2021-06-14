from celery import shared_task
from time import sleep
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail
from django.conf import settings


@shared_task
def send_single_email_task(data_dict: dict, body, context):
    sleep(5)

    # email_msg = send_mail(body, context, settings.EMAIL_HOST_USER, [data_dict.get('team_email')])
    email_msg = EmailMessage(body, context, to=[data_dict.get('team_email')])
    email_msg.content_subtype = 'html'
    email_msg.send(fail_silently=False)
    return {"status": True}


@shared_task
def send_multi_email_task(data_dict: dict, body, context):
    sleep(5)

    emails = data_dict.get('emails')

    email_msg = EmailMultiAlternatives(body, context, from_email = settings.EMAIL_HOST_USER, cc=emails)
    email_msg.content_subtype = 'html'
    email_msg.send(fail_silently=False)
    return {"status": True}

