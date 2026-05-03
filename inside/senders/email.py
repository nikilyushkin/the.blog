import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.template import loader
from premailer import Premailer

from inside.models import Subscriber

log = logging.getLogger(__name__)


def prepare_letter(html, base_url):
    html = Premailer(
        html=html,
        base_url=base_url,
        strip_important=False,
        keep_style_tags=True,
        capitalize_float_margin=True,
        cssutils_logging_level=logging.CRITICAL,
    ).transform()
    if "<!doctype" not in html:
        html = f"<!doctype html>{html}"
    return html


def send_vas3k_email(subscriber: Subscriber, subject: str, html: str, force: bool = False, **kwargs):
    if not subscriber.is_confirmed and not force:
        log.warn(f"Not sending to {subscriber.email}. Not confirmed")

    prepared_html = prepare_letter(html, base_url=f"https://{settings.APP_HOST}")

    email = EmailMessage(
        subject=subject,
        body=prepared_html,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[subscriber.email],
        headers={
            "List-Unsubscribe": f"https://{settings.APP_HOST}/unsubscribe/{subscriber.secret_hash}/"
        },
        **kwargs
    )
    email.content_subtype = "html"
    return email.send(fail_silently=False)


def send_post_newsletter(post, subscribers, subject_prefix=""):
    """Render emails/new_post.html for `post` and send to each Subscriber.

    Returns (sent_count, failures: list[(email, error_str)]).
    """
    template = loader.get_template("emails/new_post.html")
    sent = 0
    failures = []
    for subscriber in subscribers:
        html = template.render({"post": post, "subscriber": subscriber})
        try:
            send_vas3k_email(
                subscriber=subscriber,
                subject=f"{subject_prefix}{post.title}",
                html=html,
                force=True,
            )
            sent += 1
        except Exception as ex:
            failures.append((subscriber.email, str(ex)))
            log.exception(f"Newsletter send to {subscriber.email} failed")
    return sent, failures
