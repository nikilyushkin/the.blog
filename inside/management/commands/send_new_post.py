import logging
from datetime import datetime

from django.core.management import BaseCommand

from inside.models import Subscriber
from inside.senders.email import send_post_newsletter
from posts.models import Post

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send the latest visible post as a newsletter"

    def add_arguments(self, parser):
        parser.add_argument("--production", type=bool, required=False, default=False)
        parser.add_argument("--auto-confirm", type=bool, required=False, default=False)
        parser.add_argument("--test-email", type=str, required=False, default=None,
                            help="Override test recipient (default: hi@nikilyushk.in)")

    def handle(self, *args, **options):
        post = Post.visible_objects().order_by("-published_at").first()
        if not post:
            self.stdout.write("No new posts. Exiting...")
            return

        if options.get("production"):
            if post.newsletter_sent_at:
                self.stdout.write(
                    f"Newsletter for '{post.title}' already sent at {post.newsletter_sent_at}. "
                    f"Clear newsletter_sent_at in admin to resend. Exiting..."
                )
                return
            subscribers = list(Subscriber.objects.filter(is_confirmed=True))
            subject_prefix = ""
        else:
            test_email = options.get("test_email") or "hi@nikilyushk.in"
            subscribers = [
                Subscriber(email=test_email, secret_hash="test", is_confirmed=True)
            ]
            subject_prefix = "[TEST] "

        if not options.get("auto_confirm"):
            confirm = input(
                f"Send '{post.title}' to {len(subscribers)} recipient(s)? [y/N]: "
            )
            if confirm != "y":
                self.stdout.write("Not confirmed. Exiting...")
                return

        sent, failures = send_post_newsletter(post, subscribers, subject_prefix=subject_prefix)
        self.stdout.write(f"Sent {sent}/{len(subscribers)}")
        for email, err in failures:
            self.stdout.write(f"  failed: {email}: {err}")

        if options.get("production") and sent:
            post.newsletter_sent_at = datetime.utcnow()
            post.save(flush_cache=False)
            self.stdout.write(f"newsletter_sent_at = {post.newsletter_sent_at}")
