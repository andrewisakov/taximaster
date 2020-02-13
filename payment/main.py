import asyncio
import aioredis

from .config import LEGAL_SENDERS, REDIS, IMAP
from .maps import check_mailbox, idle_mailbox


@asyncio.coroutine
def _main(loop):
    redpool = yield from aioredis.create_redis_pool(REDIS)
    result = yield from check_mailbox(**IMAP)
    print(result)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(loop))
