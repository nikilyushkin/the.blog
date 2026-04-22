import pytest

from comments.models import Comment
from common.markdown.markdown import markdown_text
from heynik_blog.posts import POST_TYPES, post_config_by_type


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
