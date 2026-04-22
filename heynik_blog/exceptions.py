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
