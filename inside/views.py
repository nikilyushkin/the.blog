from django.shortcuts import render
from django.template import loader

from inside.models import Subscriber
from inside.senders.email import send_vas3k_email


def donate(request):
    return render(request, "donate.html")


def subscribe(request):
    if request.method != "POST":
        return render(request, "subscribe.html")

    antispam = request.POST.get("name")
    if antispam:
        return render(request, "error.html", {
            "title": "Spam Proetect 🛡️",
            "message": "Anti-spam check failed. "
                       "Refresh the page and try again"
        })

    email = request.POST.get("email")
    if not email or "@" not in email or "." not in email:
        return render(request, "error.html", {
            "title": "Hmmmmmm....",
            "message": "It's not an e-mail, is it?"
        })

    subscriber, is_created = Subscriber.objects.get_or_create(
        email=email,
        defaults=dict(
            secret_hash=Subscriber.generate_secret(email),
        )
    )

    if is_created:
        opt_in_template = loader.get_template("emails/opt_in.html")
        send_vas3k_email(
            subscriber=subscriber,
            subject=f"Confirmation",
            html=opt_in_template.render({
                "email": subscriber.email,
                "secret_hash": subscriber.secret_hash
            }),
            force=True,
        )

    if is_created or not subscriber.is_confirmed:
        return render(request, "message.html", {
            "title": "We need to confirm your email",
            "message": "The confirmation letter has been sent to your email. "
                       "Open it and click the button to subscribe. "
                       "Otherwise you will not receive my emails. "
                       "If there are no letters at all, check your spam/junk folder or try another email."
        })
    else:
        return render(request, "message.html", {
            "title": "You already subscribed",
            "message": "But thank you for checking :)"
        })


def confirm(request, secret_hash):
    subscriber = Subscriber.objects.filter(secret_hash=secret_hash).update(is_confirmed=True)

    if subscriber:
        return render(request, "message.html", {
            "title": "Yay! You are now subscribed",
            "message": "You will receive all the new stuff straight to your email"
        })
    else:
        return render(request, "error.html", {
            "title": "Unknown email",
            "message": "Please subscribe again"
        })


def unsubscribe(request, secret_hash):
    Subscriber.objects.filter(secret_hash=secret_hash).delete()

    return render(request, "message.html", {
        "title": "You have unsubscribed",
        "message": "I have deleted your email from the db and will not bother you anymore"
    })
