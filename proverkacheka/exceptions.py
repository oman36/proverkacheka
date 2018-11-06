class ProverkachekaBaseException(BaseException):
    pass


class InvalidQueryStringException(ProverkachekaBaseException):
    def __init__(self, query_dict: dict, keys_diff: set):
        self.query_dict = query_dict
        self.keys_diff = keys_diff

    def __str__(self):
        return f'Next query params were missed: {", ".join(self.keys_diff)}. Given {self.query_dict}.'


class InvalidStatusCodeException(ProverkachekaBaseException):
    def __init__(self, code: int, url: str = None):
        self.code = code
        self.url = url

    def __str__(self):
        return f'Returned status code {self.code} from {self.url}.'


class TicketDataNotExistsException(ProverkachekaBaseException):
    def __init__(self, url: str = None):
        self.url = url

    def __str__(self):
        return f'Ticket\'s data does not exist ({self.url}).'


class RequestTimeoutException(ProverkachekaBaseException):
    def __init__(self, timeout: float or int, url: str):
        self.url = url
        self.timeout = timeout

    def __str__(self):
        return f'Request to {self.url} takes {self.timeout} sec.'
