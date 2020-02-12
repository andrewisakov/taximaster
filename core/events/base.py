import asyncio
import json
from core import TMAPI


class BaseEvent:
    EVENT = None
    ENRICH_DATA = False
    LOGGER = None
    RED_POOL = None

    def __init__(self, payload, red_pool=None):
        self._payload = payload
        self._red_pool = red_pool or self.RED_POOL

    async def publish(self):
        with await self._red_pool as redcon:
            await redcon.publish(self.EVENT, self.payload)

    @property
    def payload(self):
        return json.dumps(self._payload)

    @classmethod
    async def save(cls, data):
        errors = []
        async with cls.PG_POOL.acquire() as pgcon:
            async with pgcon.cursor() as c:
                try:
                    data['discountedsumm'] = str(data['discountedsumm'])
                    data['source_time'] = str(data['source_time'])
                    await c.execute(('insert into order_events (order_id, event, data) '
                                    'values (%(order_id)s, %(event)s, %(data)s);'),
                                {'order_id': data.get('order_id'),
                                    'event': cls.EVENT,
                                    'data': json.dumps(data),
                                    }
                                )
                except Exception as e:
                    errors.append(str(e))
        return errors

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
            async with TMAPI.PG_POOL.acquire() as pgcon:
                async with pgcon.cursor() as c:
                    await c.execute((
                        'select o.driver_timecount, '
                        'o.discountedsumm, o.clientid as client_id, '
                        'o.driverid, o.cashless, o.state, o.phone, '
                        'cr.gosnumber, cr.color as car_color, '
                        'cr.mark as car_mark, coalesce(cr.model, \'\') as car_model, '
                        'cr.id as car_id, o.source_time '
                        'from orders o '
                        'join crews cw on (cw.id=o.crewid) '
                        'join cars cr on (cr.id=cw.carid) '
                        'where o.id=%(order_id)s;'),
                        {'order_id': data['order_id']})
                    r = await c.fetchone()
                    order_data = {cn.name :r[ix] for ix, cn in enumerate(c.description)}
                    data.update(**order_data)
        return data


async def register(loop, redcon, redpool, logger):
    channels = []
    for cls in BaseEvent.__subclasses__():
        if cls.EVENT:
            channel = await redcon.subscribe(cls.EVENT)
            channels.append(asyncio.ensure_future(
                cls.channel_reader(channel[0]), loop=loop))
            cls.LOGGER = logger
            cls.RED_POOL = redpool
            cls.PG_POOL = loop.pg_pool
            logger.debug('Event %s registered %s', cls.EVENT, channel)
    logger.info('%s events registered.', len(channels))
    return channels


async def unregister(channels, redcon, logger):
    logger.info('%s events unregistering.', len(channels))
    await redcon.unsubscribe(*[ch for ch in channels.keys()])
    logger.info('%s events unregistered.', len(channels))
