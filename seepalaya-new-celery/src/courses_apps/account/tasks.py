import logging
from celery import shared_task
# from celery.utils.log import get_task_logger
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger('django.errors')


@shared_task(bind=True, name='send_email_task')
def send_email_task(self, subject, message, email_to):
    try:
        print('sending email')
        print(f"email:{email_to}")
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email_to], fail_silently=False)
    except Exception as e:
        logger.error('CELERY - Exception raised while sending email')
        raise self.retry(exc=e, countdown=60)
