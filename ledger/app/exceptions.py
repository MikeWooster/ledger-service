import json

from werkzeug.exceptions import HTTPException as BaseHTTPException


class HTTPException(BaseHTTPException):
    def get_headers(self, environ=None):
        # Override headers so that we always return errors as json
        return [("Content-Type", "application/json")]

    def get_description(self, environ=None):
        return self.description

    def get_body(self, environ=None):
        return json.dumps(
            {"error": {"code": self.code, "name": self.name, "description": self.get_description(environ)}}
        )


class BadRequest(HTTPException):
    code = 400
    description = "The browser (or proxy) sent a request that this server could " "not understand XXX."
