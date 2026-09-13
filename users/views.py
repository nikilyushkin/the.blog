from django.http import HttpResponse
from django.shortcuts import render, redirect

from users.forms import UserEditForm


def profile(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = UserEditForm(instance=request.user)

    return render(request, "users/profile.html", {
        "form": form,
    })


AI_CRAWLERS = [
    "GPTBot",
    "OAI-SearchBot",
    "ChatGPT-User",
    "ClaudeBot",
    "Claude-SearchBot",
    "Claude-User",
    "anthropic-ai",
    "Google-Extended",
    "PerplexityBot",
    "Perplexity-User",
    "Applebot-Extended",
    "CCBot",
    "meta-externalagent",
]


def robots(request):
    rules = [
        "Content-Signal: search=yes, ai-input=yes, ai-train=yes",
        "Allow: /",
        "Disallow: /clickers/",
        "Disallow: /auth/",
    ]
    lines = [
        "User-agent: *",
        *rules,
        "Clean-param: comment_order&goto&preview /",
        "",
        # a named group overrides "*", so AI bots get the same rules explicitly
        *[f"User-agent: {bot}" for bot in AI_CRAWLERS],
        *rules,
        "",
        f"Host: https://{request.get_host()}",
        f"Sitemap: https://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
