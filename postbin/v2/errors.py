from typing import Union
try:
    from requests import Response
except ImportError:
    Response = None

try:
    from aiohttp import ClientResponse
except ImportError:
    ClientResponse = None
#

class HTTPException(Exception):
    """
    Represents a HTTP Exception.

    Attributes:
        response - Union[ClientResponse, Response]: the response that was returned.
        message - Optional[str]: A custom message as to why the error was raised.
        status - int: The resolved status (so you don't have to dig between the two classes)
    """
    def __init__(self, response: Union[Response, None, ClientResponse], *args, message: str = None, **kwargs):
        """
        Creates the HTTPException

        :param response: the Response object
        :param args: args to pass to super
        :param message: a custom message as to why the error was raised
        :param kwargs: doesn't seem like much to me.
        """
        super().__init__(kwargs, *args)
        self.response = response
        self.message = message
        try:
            self.status = response.status if isinstance(response, ClientResponse) else response.status_code
        except AttributeError:
            self.status = -1  # response was None.

    def __str__(self):
        if self.message:
            return self.__class__.__name__ + ": " + self.message  # for dynamic stuff
        return "{0.__class__.__name__}: Got status {0.status} on URL {0.response.url}.".format(self)

    def __repr__(self):
        return f"{self.__class__.__name__}(response={self.response} message={self.message} status={self.status})"

class FailedTest(HTTPException):
    """
    Raised when a URL test fails.
    """
    pass

class OfflineServer(HTTPException):
    """The server provided wasn't online or valid."""
