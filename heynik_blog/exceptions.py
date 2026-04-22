class BlogException(Exception):
    default_code = "error"
    default_title = "Something is wrong"
    default_message = "Noone knows what is wrong though :("

    def __init__(self, code=None, title=None, message=None, data=None):
        self.code = code or self.default_code
        self.title = title or self.default_title
        self.message = message or self.default_message
        self.data = data or {}


class BadRequest(BlogException):
    default_code = "bad-request"
    default_title = "Bad request"
    default_message = "Something is broken again"


class NotFound(BlogException):
    default_code = "not-found"
    default_title = "Not Found"
    default_message = ""


class AccessDenied(BlogException):
    default_code = "access-forbidden"
    default_title = "You can't be here"
    default_message = "Naughty, naughty!"


class RateLimitException(BlogException):
    default_code = "rate-limit"
    default_title = "You have created too many posts or comments today"
    default_message = "Please, stop."


class ContentDuplicated(BlogException):
    default_code = "duplicated-content"
    default_title = "Hm..."
    default_message = "It seems you are trying to post the same thing again. Please check if everything is alright."


class InsufficientFunds(BlogException):
    default_code = "insufficient-funds"
    default_title = "Insufficient Funds"


class URLParsingException(BlogException):
    default_code = "url-parser-exception"
    default_title = "URL Parser has failed"
    default_message = ""


class InvalidCode(BlogException):
    default_code = "invalid-code"
    default_title = "Invalid Code"
    default_message = "Enter it or request it again. After several incorrect attempts, codes are deleted"


class ApiInsufficientFunds(BlogException):
    default_code = "api-insufficient-funds"
    default_title = "Insufficient Funds"


class ApiException(BlogException):
    default_message = None


class ApiBadRequest(BlogException):
    default_code = "bad-request"
    default_title = "Bad Request"


class ApiAuthRequired(ApiException):
    default_code = "api-authn-required"
    default_title = "Auth Required"


class ApiAccessDenied(ApiException):
    default_code = "api-access-denied"
    default_title = "Access Denied"

