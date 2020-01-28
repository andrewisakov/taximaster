import json
from functools import lru_cache
import psycopg2
import xmltodict
from core.utils.json import get_value
from settings import DSN


def load_events():
    EVENTS = []
    with psycopg2.connect(DSN) as db:
        with db.cursor() as c:
            c.execute(
                'select settings from order_states where settings is not null;')
            for row in c:
                sets = xmltodict.parse(row[0])
                if int(get_value('settings.oktell.to_client.use_call_back', sets)):
                    event_name = get_value(
                        'settings.oktell.to_client.script_name', sets).upper()
                    if event_name:
                        EVENTS.append(event_name)
    return EVENTS


class BaseHandler:
    EVENT = 'CALLBACK_ORIGINATE_ACCEPTED'

    @classmethod
    async def handle(cls, data, app, logger):
        message = {
            'order_id': data['order_id'],
            'state': data['callback_state'],
        }
        await cls.publish(cls.EVENT, message, app, logger)

    @classmethod
    async def publish(cls, event, message, app, logger):
        with await app['redis'] as redcon:
            redcon.publish(event, json.dumps(message))
            logger.debug('Publish %s: %s', event, message)


class OrderEvent(BaseHandler):
    EVENTS = load_events()

    @classmethod
    async def handle(cls, data, app, logger):
        await super().handle(data, app, logger)
        event = 'OKTELL_{}'.format(data['event'].upper())
        message = {
            'order_id': data['order_id'],
            'phones': (data['phone1'], ),
        }
        await cls.publish(event, message, app, logger)


class TMABConnect(BaseHandler):
    EVENTS = ('TMABCONNECT', )
    @classmethod
    async def handle(cls, data, app, logger):
        event = 'OKTELL_'.format(data['event'])
        message = {
            'order_id': data['order_id'],
            'phones': (data['phone1'], data['phone2'], ),
        }
        await cls.publish(event, message, app, logger)


@lru_cache(maxsize=100)
def select_handlers(event):
    # return [cls.handle for cls in BaseHandler.__subclasses__() if event.upper() in cls.EVENTS]
    result = []
    for cls in BaseHandler.__subclasses__():
        if event.upper() in cls.EVENTS:
            result.append(cls.handle)
    return result
