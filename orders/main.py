import logging
import aioredis
import asyncio
import aiopg
from .handlers import register, unregister
from .config import DSN, REDIS, CALLBACK_STOP


LOGGER = logging.getLogger()


async def _main(loop):
    LOGGER.debug('Starting service')
    redpool = await aioredis.create_redis_pool(REDIS)
    loop.pg_pool = await aiopg.create_pool(**DSN)
    with await redpool as redcon:
        channels = await register(loop, redcon, LOGGER)
        for channel in channels:
            channel.CALLBACK_STOP = CALLBACK_STOP
        channels = await asyncio.gather(*channels)
        await unregister(channels)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(loop))
