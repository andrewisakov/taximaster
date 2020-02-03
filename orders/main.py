import logging
import aioredis
import asyncio
import aiopg
from .handlers import register, unregister, TMAPI
from .config import DSN, REDIS, CALLBACK_STOP, TMTAPI


LOGGER = logging.getLogger()


async def _main(loop):
    LOGGER.debug('Starting service')
    redpool = await aioredis.create_redis_pool(REDIS)
    loop.pg_pool = await aiopg.create_pool(**DSN)
    TMAPI.TM_HOST, TMAPI.TM_PORT, TMAPI.TM_SOLT, TMAPI.PG_POOL = TMTAPI.get(
        'host'), TMTAPI.get('port'), TMTAPI.get('solt'), loop.pg_pool
    with await redpool as redcon:
        channels = await register(loop, redcon, LOGGER)
        for channel in channels:
            channel.CALLBACK_STOP = CALLBACK_STOP
        channels = await asyncio.gather(*channels)
        await unregister(channels)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(loop))
