import asyncio
import json
from core import TMAPI


class BaseEvent:
    EVENT = None
    ENRICH_DATA = False
    LOGGER = None

    def __init__(self, payload, publisher=None):
        self._payload = payload
        self._publisher = publisher or self.REDCON

    async def publish(self):
        self.REDCON.publish(self.EVENT, self.payload)

    @property
    def payload(self):
        return json.dumps(self._payload)

    @classmethod
    async def save(cls, data):
        async with cls.PG_POOL.acquire() as pgcon:
            async with pgcon.cursor() as c:
                await c.excute(('insert into events (order_id, event, data) '
                                'values (%(order_id)s, %(event)s, %(data)s);'),
                               {'order_id': data.get('order_id'),
                                'event': cls.EVENT,
                                'data': data,
                                }
                               )

    @classmethod
    async def handle(cls, data):
        data = await cls.tmapi_request(data)
        return data

    @classmethod
    async def channel_reader(cls, channel):
        while await channel.wait_message():
            message = await channel.get_json()
            cls.LOGGER.debug('Got %s: %s', channel.name, message)
            result = await cls.handle(message)

    @classmethod
    async def tmapi_request(cls, data):
        result = {}
        if cls.ENRICH_DATA:
            cls.LOGGER.debug('Enrich order %s data.', data['order_id'])
            order_state = TMAPI.get_order_state(data)
            order_info = TMAPI.get_info_by_order_id(
                {**data,
                 'fields': ('DRIVER_TIMECOUNT-'
                            'SUMM-'
                            'SUMCITY-'
                            'DISCOUNTEDSUMM-'
                            'SUMCOUNTRY-'
                            'SUMIDLETIME-'
                            'CASHLESS-'
                            'CLIENT_ID'),
                 })
            # Консолидидация результатов двух запросов. Кривизна TM API...
            result = order_state['data'].update(order_info['data'])
        return result


async def register(loop, redcon, logger):
    channels = []
    for cls in BaseEvent.__subclasses__():
        if cls.EVENT:
            channel = await redcon.subscribe(cls.EVENT)
            channels.append(asyncio.ensure_future(
                cls.channel_reader(channel[0]), loop=loop))
            cls.LOGGER = logger
            cls.REDCON = redcon
            cls.PGPOOL = loop.pg_pool
            logger.debug('Event %s registered %s', cls.EVENT, channel)
    logger.info('%s events registered.', len(channels))
    return channels


async def unregister(channels, redcon, logger):
    logger.info('%s events unregistering.', len(channels))
    await redcon.unsubscribe(*[ch for ch in channels.keys()])
    logger.info('%s events unregistered.', len(channels))
