import asyncio
import aioredis
import logging
import settings
from core.events.base import register, unregister


LOGGER = logging.getLogger('tmapi')


async def _main(loop):
    LOGGER.debug('Starting service')
    redpool = await aioredis.create_redis_pool(settings.REDIS_HOST)
    with await redpool as redcon:
        channels = await register(loop, redcon, LOGGER)
        channels = await asyncio.gather(*channels)
        await unregister(channels)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(loop))
