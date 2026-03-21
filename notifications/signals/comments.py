import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from comments.models import Comment
from notifications.telegram.bot import bot

log = logging.getLogger(__name__)


@receiver(post_save, sender=Comment)
def create_comment(sender, instance, created, **kwargs):
    if not created:
        return  # skip updates

    if not bot:
        return

    comment = instance
    post = comment.post

    link = f"https://{settings.APP_HOST}/{post.type}/{post.slug}/"

    if not post.is_published():
        link += "?preview=1"

    if comment.block:
        link += f"#block-{comment.block}-{comment.id}"
    else:
        link += f"#comment-{comment.id}"

    full_text = f"💬 <b>{comment.author_name}</b> ➜ <a href='{link}'>{post.title}</a>:\n\n{comment.text[:2000]}"

    try:
        bot.send_message(
            chat_id=settings.TELEGRAM_MAIN_CHAT_ID,
            text=full_text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except Exception:
        log.exception("Failed to send telegram notification")
