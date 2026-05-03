import re

from django import template
from django.conf import settings

register = template.Library()

# Matches the 10-char ASIN/ISBN-10 across the common Amazon URL shapes:
#   /dp/B0XXXXXXXX
#   /gp/product/B0XXXXXXXX
#   /exec/obidos/asin/B0XXXXXXXX
#   /-/dp/B0XXXXXXXX
ASIN_RE = re.compile(r"/(?:dp|gp/product|exec/obidos/asin|-/[^/]+/dp)/([A-Z0-9]{10})", re.I)


@register.filter
def amazon_asin(url):
    """Return the ASIN (or ISBN-10) parsed from an Amazon URL, or empty string."""
    if not url:
        return ""
    match = ASIN_RE.search(url)
    return match.group(1) if match else ""


@register.filter
def amazon_cover(url):
    """Return Amazon's hotlinkable cover image URL for an Amazon product URL.

    Uses the predictable images-na endpoint that doesn't require PAAPI.
    """
    asin = amazon_asin(url)
    if not asin:
        return ""
    return f"https://images-na.ssl-images-amazon.com/images/P/{asin}.jpg"


@register.filter
def amazon_buy(url):
    """Return a clean Amazon product URL, with affiliate tag appended if configured.

    Falls back to the original URL if no ASIN can be parsed.
    """
    asin = amazon_asin(url)
    if not asin:
        return url or ""
    tag = getattr(settings, "AMAZON_AFFILIATE_TAG", "") or ""
    suffix = f"?tag={tag}" if tag else ""
    return f"https://www.amazon.com/dp/{asin}/{suffix}"
