import asyncio
import aiopg
import aioredis
import logging
from .config import DSN, REDIS
from .handlers import register, unregister


LOGGER = logging.getLogger('tmapi')


async def _main(loop):
    LOGGER.debug('Starting service')
    redpool = await aioredis.create_redis_pool(REDIS)
    loop.pg_pool = await aiopg.create_pool(**DSN)
    with await redpool as redcon:
        channels = await register(loop, redcon, LOGGER)
        channels = await asyncio.gather(*channels)
        await unregister(channels, redcon, LOGGER)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(loop))
