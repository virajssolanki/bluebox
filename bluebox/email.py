from django.core.mail import send_mail
from django.http.response import BadHeaderError
from django.conf import settings
from django.template.loader import render_to_string


def send_email(email_list, subject, template_name, context):

    msg_html = render_to_string(template_name, context)
    try:
        send_mail(
            subject = subject,
            html_message = msg_html,
            message = msg_html,
            from_email = settings.DEFAULT_FROM_EMAIL,
            recipient_list = email_list,
            fail_silently = True
        )
        return ('success your email has been sent')
    except BadHeaderError as e:
            print("erorr in email:", e)
            raise e