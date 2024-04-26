import logging
from urllib.parse import urlencode, urlparse

from authlib.integrations.base_client import OAuthError
from django.conf import settings
from django.contrib.auth import logout, login
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from requests import HTTPError

from users.models import User

log = logging.getLogger(__name__)


def log_in(request):
    return render(request, "users/login.html")


def log_out(request):
    logout(request)
    return redirect("index")


