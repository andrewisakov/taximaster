import logging
import aioredis
import asyncio
import aiopg
from .handlers import register, unregister, TMAPI
from .config import DSN, REDIS, CALLBACK_STOP, TMTAPI, TME_DB, INIT
from .database import AsteriskSounds, init, TABLES


LOGGER = logging.getLogger()


async def _main(loop):
    LOGGER.debug('Starting service')
    result = init(INIT, DSN, TABLES)
    redpool = await aioredis.create_redis_pool(REDIS, maxsize=50)
    loop.pg_pool = await aiopg.create_pool(**DSN)
    TMAPI.TM_HOST, TMAPI.TM_PORT, TMAPI.TM_SOLT, TMAPI.PG_POOL, \
        TMAPI.LOGGER, TMAPI.RED_POOL = TMTAPI.get(
            'host'), TMTAPI.get('port'), TMTAPI.get('solt'), (
            await aiopg.create_pool(**TME_DB)), LOGGER, redpool
    TMAPI.ASTERISK_SOUNDS = AsteriskSounds()

    with await redpool as redcon:
        channels = await register(loop, redcon, redpool, LOGGER)
        for channel in channels:
            channel.CALLBACK_STOP = CALLBACK_STOP
        channels = await asyncio.gather(*channels)
        await unregister(channels)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(loop))
