import asyncio
import aiopg
import aioredis
import logging
from .config import DSN, REDIS, TMTAPI
from .handlers import register, unregister, TMAPI


LOGGER = logging.getLogger('tmapi')


async def _main(loop):
    LOGGER.debug('Starting service')
    redpool = await aioredis.create_redis_pool(REDIS, maxsize=50)
    loop.pg_pool = await aiopg.create_pool(**DSN)
    TMAPI.TM_HOST, TMAPI.TM_PORT, TMAPI.TM_SOLT, PG_POOL = TMTAPI.get(
        'host'), TMTAPI.get('port'), TMTAPI.get('solt'), loop.pg_pool

    with await redpool as redcon:
        channels = await register(loop, redcon, redpool, LOGGER)
        channels = await asyncio.gather(*channels)
        await unregister(channels, redcon, LOGGER)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(loop))
