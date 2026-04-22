# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

Fork of the vas3k.ru blog codebase, rebranded as `heynik.blog`. Single-tenant author blog (Nik ILyushkin), not built for multi-tenant or scale. The README explicitly disclaims support and scalability — treat it as a personal site with opinionated legacy choices.

## Stack

- Python 3.10+/3.11+, Django 4.2, PostgreSQL 15
- Poetry for dependency management (`pyproject.toml` / `poetry.lock`)
- Frontend: htmx + vanilla JS, no bundler, no CSS framework; templates in `frontend/html/`, static in `frontend/static/`
- Markdown rendering via `mistune` with custom plugins in `common/markdown/plugins/`
- Production: gunicorn + uvicorn workers, Sentry, SMTP via AWS SES, Telegram notifications

## Common commands

Local (Poetry on host):
```
poetry install
poetry run python3 manage.py migrate
make run-dev                      # runserver on 0.0.0.0:8000
poetry run pytest                 # run test suite
poetry run pytest path/to/tests.py::TestClass::test_method   # single test
poetry run python3 manage.py <cmd>  # any Django management command
```

Docker (preferred for parity with CI):
```
docker compose up                 # builds app + postgres, runs migrations, serves on :8000
docker compose exec -T blog_app make migrate
docker compose exec -T blog_app poetry run pytest --tb=short -q
```

The compose service is named `blog_app` (matches `docker-compose.production.yml` and CI). The legacy name `club_app` was retired in favor of a single consistent name.

CI (`.github/workflows/check_build_and_run.yml`) runs `docker compose up -d`, waits for the app container, then runs `make migrate` and `pytest` inside it — tests are expected to pass against a real Postgres, not mocks.

## Testing

- `pytest-django` with settings pinned in `pyproject.toml` (`[tool.pytest.ini_options]`).
- `conftest.py` at repo root provides `post`, `user`, `authed_client` fixtures — build on these instead of reconstructing Post/User in each test (Post needs explicit `created_at`, Comment creation requires an authenticated user).
- `tests/test_smoke.py` is the safety-net suite: markdown pipeline, post-type registry, index/show_post/list/robots/sitemap responses, html_cache population, comment creation + counter. Don't delete these — they're the boundary tests a refactor needs to stay honest.
- Tests run against the real Postgres (container or host). `--reuse-db` is on by default; pass `--create-db` the first time or after model changes.
- Custom `Vas3kRenderer` emits `<div class="header-1">` instead of `<h1>` — assert on `class="header-1"`, not tag name.

Database: create an empty Postgres DB named `vas3k_blog` before first `migrate` if running outside Docker. The DB name is legacy — kept as-is to avoid a production data migration; the Python module was renamed to `heynik_blog`, but the DB, the `POSTGRES_DB` env var, and the `vas3k_club_slug` column on `users.User` still carry the old name. Default credentials come from env vars (`POSTGRES_DB/USER/PASSWORD/HOST/PORT`) with localhost/postgres fallbacks in `heynik_blog/settings.py`.

One-shot data migration from the legacy DB: set `MIGRATE=<old_db_name>` to register the `old` connection, then `poetry run python3 manage.py migrate_old_posts` (see `posts/management/commands/migrate_old_posts.py`).

## Architecture

Django project root is `heynik_blog/` (settings, `urls.py`, ASGI/WSGI). Domain is split across per-feature apps, each a standard Django app (`models.py`, `views.py`, `admin.py`, `migrations/`):

- `posts/` — core content model. Single `Post` table (`posts/models.py`) keyed by `slug`, discriminated by `type` (see below). `renderers.py` turns the stored markdown `text` into cached `html_cache`.
- `heynik_blog/posts.py` — **post-type registry**. Declares the valid `type` values (`blog`, `thoughts`, `books`, `gallery`, `inside`, `notes`) and the card/list/show templates each one uses. Adding a new post type means editing this file, not a DB migration.
- `common/markdown/` — mistune-based rendering pipeline. `markdown.py` wires the renderer (`club_renderer` / `email_renderer` / `plain_renderer`) with custom block plugins (`cite_block`, `media_block`, `spoiler`, `text_block`). Post content uses a bespoke `[[[ ... ]]]` block syntax — see `migrate_old_posts.parse_text` for the wrapping convention.
- `comments/`, `clickers/` (reactions on comments/blocks), `rss/` (Full/Public/Private feeds), `inside/` (donate + newsletter subscribe/confirm/unsubscribe), `authn/` (login, legacy Club OpenID and Patreon integrations mostly commented out), `users/` (custom `AUTH_USER_MODEL = "users.User"`, profile, `robots.txt`), `notifications/` (Telegram bot + Django signals that forward comment events).
- `utils/` — shared helpers (`slug`, `wait_for_postgres`, etc.); not a Django app.

Routing (`heynik_blog/urls.py`) is deliberately terse: most content is served by the catch-all `<post_type>/<post_slug>/` and `<post_type>/` patterns at the bottom, so any new top-level path must be added **before** those two lines or it will be swallowed.

Templates live outside the apps in `frontend/html/{index,posts,comments,emails,users,common,clickers}/`. The post-type registry (`POST_TYPES`) points into `posts/cards/`, `posts/lists/`, `posts/full/` subtrees — templates are keyed by type, not inherited via app config.

## Deployment

`.github/workflows/deploy.yml` runs on push to `main`: builds an ARM64 image, pushes to `ghcr.io/<actor>/blog`, rsyncs the repo to the production host, and runs `docker compose -f docker-compose.production.yml up -d` over SSH. Secrets are injected into `.env` at deploy time. `GITHUB_SHA` is used as `STYLES_HASH` for cache-busting static assets.
