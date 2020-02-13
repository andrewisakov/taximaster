import asyncio
import datetime
from .parsers import parse_body, parse_header
import aioimaplib


@asyncio.coroutine
def check_mailbox(host, port, user, password, inbox):
    imap = aioimaplib.IMAP4_SSL(host=host)
    hello = yield from imap.wait_hello_from_server()
    response = yield from imap.login(user, password)
    if response.result != 'OK':
        raise
    since = '-'.join(str(datetime.datetime.now().date()).split('-')[::-1])
    select = yield from imap.select(inbox, readonly=True)
    res, data = yield from imap.search(None, f'(SINCE {since}')
    if res != 'OK':
        raise
    return data


async def idle_mailbox(host, port, user, password, inbox):
    pass
