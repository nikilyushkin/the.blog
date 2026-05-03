from datetime import datetime

import pytest

from comments.models import Comment
from common.markdown.markdown import markdown_text
from heynik_blog.posts import POST_TYPES, post_config_by_type
from posts.models import Post


def test_markdown_pipeline_produces_html():
    html = markdown_text("# Hello\n\nThis is **bold**.")
    assert "header-1" in html  # Vas3kRenderer emits <div class="header-1">
    assert "<strong>" in html


def test_post_type_registry_is_coherent():
    for type_name, config in POST_TYPES.items():
        assert config.name
        assert config.show_template.endswith(".html")
        assert post_config_by_type(type_name) is config


def test_post_type_registry_unknown_returns_default():
    config = post_config_by_type("nonexistent")
    assert config.name == "Posts"


def test_index_returns_200(client, post):
    response = client.get("/")
    assert response.status_code == 200


def test_show_post_renders_and_populates_html_cache(client, post):
    assert post.html_cache is None

    response = client.get(f"/blog/{post.slug}/")
    assert response.status_code == 200

    post.refresh_from_db()
    assert post.html_cache, "show_post must populate html_cache as a side-effect"
    assert "<strong>" in post.html_cache


def test_show_post_wrong_type_redirects_to_canonical(client, post):
    response = client.get(f"/notes/{post.slug}/")
    assert response.status_code in (301, 302)
    assert f"/blog/{post.slug}/" in response["Location"]


def test_show_post_unknown_slug_returns_404(client, db):
    response = client.get("/blog/does-not-exist/")
    assert response.status_code == 404


def test_list_posts_unknown_type_returns_404(client, db):
    response = client.get("/nonexistent-type/")
    assert response.status_code == 404


def test_robots_txt_served(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert b"User-agent: *" in response.content


def test_sitemap_xml_served(client, post):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert b"hello-world" in response.content


def test_create_comment_increments_post_counter(authed_client, post):
    assert post.comment_count == 0

    response = authed_client.post("/comments/create/", {
        "post_slug": post.slug,
        "text": "Nice post, thanks!",
    })
    assert response.status_code == 200

    assert Comment.objects.filter(post=post).count() == 1

    post.refresh_from_db()
    assert post.comment_count == 1


def test_create_comment_requires_min_length(authed_client, post):
    response = authed_client.post("/comments/create/", {
        "post_slug": post.slug,
        "text": "hi",
    })
    assert response.status_code == 400
    assert Comment.objects.filter(post=post).count() == 0


@pytest.fixture
def stream_post(db):
    return Post.objects.create(
        type="stream",
        slug="quick-thought",
        author="nik",
        title="A quick thought",
        subtitle="Something short to share",
        text="Just a short note. Nothing fancy here.",
        created_at=datetime.utcnow(),
        is_visible=True,
        is_visible_on_home_page=True,
    )


def test_stream_list_returns_200(client, stream_post):
    response = client.get("/stream/")
    assert response.status_code == 200
    assert b"A quick thought" in response.content
    assert b"feed-list" in response.content


def test_stream_show_post_renders_flat_layout(client, stream_post):
    response = client.get(f"/stream/{stream_post.slug}/")
    assert response.status_code == 200
    assert b"feed-full-title" in response.content
    assert b"A quick thought" in response.content


def test_index_includes_stream_section(client, stream_post):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Stream" in response.content
    assert b"A quick thought" in response.content


@pytest.fixture
def book_post_no_data(db):
    return Post.objects.create(
        type="books",
        slug="test-book",
        author="nik",
        title="Test Book",
        text="[[[\n\nContent.\n\n]]]",
        created_at=datetime.utcnow(),
        is_visible=True,
        data=None,
    )


def test_books_show_post_no_data_renders_200(client, book_post_no_data):
    response = client.get(f"/books/{book_post_no_data.slug}/")
    assert response.status_code == 200
    assert b"book-headline" in response.content
    assert b"Test Book" in response.content


def test_books_list_with_no_data_renders_200(client, book_post_no_data):
    response = client.get("/books/")
    assert response.status_code == 200
    assert b"book-card" in response.content


def test_show_post_metadata_is_in_english(client, post):
    response = client.get(f"/blog/{post.slug}/")
    assert response.status_code == 200
    body = response.content
    assert b"\xd0\xba\xd0\xbe\xd0\xbc\xd0\xbc\xd0\xb5\xd0\xbd\xd1\x82" not in body  # no "коммент"
    assert b"\xd0\xbf\xd1\x80\xd0\xbe\xd1\x81\xd0\xbc\xd0\xbe\xd1\x82\xd1\x80" not in body  # no "просмотр"
