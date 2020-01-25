import pprint
import inspect
from .models import REQUESTS


def request_parser(payload):
    caller = inspect.stack()[1]
    return {v: payload.get(k)
            for k, v in REQUESTS.get(caller.function, {}).items()}
