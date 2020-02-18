import asyncio
import aioredis
import logging

from .config import REDIS, IMAP
from .maps import mail_stream, DriverOperCreate


LOGGER = logging.getLogger()


async def _main(loop):
    loop.set_debug(True)
    DriverOperCreate.RED_POOL = await aioredis.create_redis_pool(REDIS)
    result = await mail_stream(**IMAP, loop=loop, logger=LOGGER)
    print(result)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(loop))
