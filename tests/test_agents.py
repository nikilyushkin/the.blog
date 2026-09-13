def test_robots_txt_has_content_signals_and_ai_crawlers(client):
    response = client.get("/robots.txt")
    assert b"Content-Signal: search=yes, ai-input=yes, ai-train=yes" in response.content
    assert b"User-agent: GPTBot" in response.content
    assert b"User-agent: ClaudeBot" in response.content


def test_show_post_returns_markdown_on_request(client, post):
    response = client.get(f"/blog/{post.slug}/", HTTP_ACCEPT="text/markdown")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/markdown")
    assert response["Vary"] == "Accept"
    assert b"# Hello World" in response.content
    assert b"This is a **test** post." in response.content


def test_index_returns_markdown_on_request(client, post):
    response = client.get("/", HTTP_ACCEPT="text/markdown")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/markdown")
    assert b"[Hello World](https://testserver/blog/hello-world/)" in response.content


def test_index_markdown_hides_members_only_posts(client, post):
    post.is_members_only = True
    post.save()
    response = client.get("/", HTTP_ACCEPT="text/markdown")
    assert b"Hello World" not in response.content


def test_show_post_returns_html_for_browsers(client, post):
    response = client.get(
        f"/blog/{post.slug}/",
        HTTP_ACCEPT="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    )
    assert response["Content-Type"].startswith("text/html")


def test_members_only_post_is_not_leaked_as_markdown(client, post):
    post.is_members_only = True
    post.save()
    response = client.get(f"/blog/{post.slug}/", HTTP_ACCEPT="text/markdown")
    assert not response["Content-Type"].startswith("text/markdown")
