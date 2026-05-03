from datetime import datetime

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html

from inside.models import Subscriber
from inside.senders.email import send_post_newsletter
from posts.models import Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title", "slug", "type", "created_at",
        "published_at", "comment_count", "view_count",
        "is_visible", "newsletter_status",
    )
    ordering = ("-created_at",)
    change_form_template = "admin/posts/post/change_form.html"

    def newsletter_status(self, obj):
        if obj.newsletter_sent_at:
            return format_html(
                '<span style="color:#1b8a3a;">Sent {}</span>',
                obj.newsletter_sent_at.strftime("%Y-%m-%d %H:%M"),
            )
        return format_html('<span style="color:#888;">—</span>')
    newsletter_status.short_description = "Newsletter"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<uuid:object_id>/send-newsletter/",
                self.admin_site.admin_view(self.send_newsletter_view),
                name="posts_post_send_newsletter",
            ),
            path(
                "<uuid:object_id>/send-test-newsletter/",
                self.admin_site.admin_view(self.send_test_newsletter_view),
                name="posts_post_send_test_newsletter",
            ),
        ]
        return custom + urls

    def send_newsletter_view(self, request, object_id):
        if not request.user.is_superuser:
            messages.error(request, "Superuser only.")
            return self._back(object_id)

        post = self.get_object(request, object_id)
        if not post:
            messages.error(request, "Post not found.")
            return self._back(object_id)

        if post.newsletter_sent_at:
            messages.error(
                request,
                f"Newsletter for this post was already sent on "
                f"{post.newsletter_sent_at.strftime('%Y-%m-%d %H:%M')} UTC. "
                f"Clear the timestamp in the form below if you really need to resend.",
            )
            return self._back(object_id)

        subscribers = Subscriber.objects.filter(is_confirmed=True)
        total = subscribers.count()
        if total == 0:
            messages.warning(request, "No confirmed subscribers — nothing sent.")
            return self._back(object_id)

        sent, failures = send_post_newsletter(post, subscribers)

        post.newsletter_sent_at = datetime.utcnow()
        post.save(flush_cache=False)

        if failures:
            messages.warning(
                request,
                f"Sent to {sent}/{total}. Failures: " +
                ", ".join(f"{email} ({err})" for email, err in failures[:5]) +
                (f" (+{len(failures) - 5} more)" if len(failures) > 5 else ""),
            )
        else:
            messages.success(request, f"Newsletter sent to {sent} subscribers.")

        return self._back(object_id)

    def send_test_newsletter_view(self, request, object_id):
        if not request.user.is_superuser:
            messages.error(request, "Superuser only.")
            return self._back(object_id)

        post = self.get_object(request, object_id)
        if not post:
            messages.error(request, "Post not found.")
            return self._back(object_id)

        test_email = request.user.email
        test_subscriber = Subscriber(
            email=test_email,
            secret_hash="test",
            is_confirmed=True,
        )
        sent, failures = send_post_newsletter(
            post, [test_subscriber], subject_prefix="[TEST] "
        )

        if failures:
            messages.error(request, f"Test send to {test_email} failed: {failures[0][1]}")
        else:
            messages.success(request, f"Test newsletter sent to {test_email}.")

        return self._back(object_id)

    def _back(self, object_id):
        return HttpResponseRedirect(
            reverse("admin:posts_post_change", args=[object_id])
        )


admin.site.register(Post, PostAdmin)
