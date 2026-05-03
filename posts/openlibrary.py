import json
import logging
import re
import urllib.request

log = logging.getLogger(__name__)


def fetch_book_metadata(isbn):
    """Fetch book metadata from Open Library by ISBN-10/13.

    Returns dict with optional keys: author, year, pages.
    Returns empty dict on any failure (network, missing data, etc.).
    """
    if not isbn:
        return {}

    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "heynik.blog/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            payload = json.loads(response.read())
    except Exception as ex:
        log.warning(f"Open Library lookup for ISBN={isbn} failed: {ex}")
        return {}

    book = payload.get(f"ISBN:{isbn}") or {}
    if not book:
        return {}

    result = {}

    authors = book.get("authors") or []
    names = [a.get("name") for a in authors if a.get("name")]
    if names:
        result["author"] = ", ".join(names)

    publish_date = book.get("publish_date") or ""
    year_match = re.search(r"\d{4}", publish_date)
    if year_match:
        result["year"] = int(year_match.group())

    pages = book.get("number_of_pages")
    if pages:
        result["pages"] = int(pages)

    return result
