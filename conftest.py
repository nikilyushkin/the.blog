from datetime import datetime

import pytest
from django.test import Client

from posts.models import Post
from users.models import User


@pytest.fixture
def post(db):
    return Post.objects.create(
        type="blog",
        slug="hello-world",
        author="nik",
        title="Hello World",
        text="# Hello\n\nThis is a **test** post.",
        created_at=datetime.utcnow(),
        is_visible=True,
    )


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="tester",
        email="tester@example.com",
        password="test-pass",
    )


@pytest.fixture
def authed_client(user):
    c = Client()
    c.force_login(user)
    return c
