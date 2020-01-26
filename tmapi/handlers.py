import json
from functools import lru_cache


class BaseHandler:
    EVENT = 'CALLBACK_ORIGINATE_ACCEPTED'

    @classmethod
    async def handle(cls, data, app):
        message = {
            'order_id': data['order_id'],
            'state': data['callback_state'],
        }
        await cls.publish(cls.EVENT, message, app)

    @classmethod
    async def publish(cls, event, message, app):
        with await app['redis'] as redcon:
            print(event, message)
            redcon.publish(event, json.dumps(message))


class OrderEvent(BaseHandler):
    EVENTS = ('ORDER_ASSIGNED',)
    @classmethod
    async def handle(cls, data, app):
        await super().handle(data, app)
        event = 'OKTELL_{}'.format(data['event'].upper())
        message = {
            'order_id': data['order_id'],
            'phones': (data['phone1'], ),
        }
        await cls.publish(event, message, app)


class TMABConnect(BaseHandler):
    EVENTS = ('TMABCONNECT', )
    @classmethod
    async def handle(cls, data, app):
        event = 'OKTELL_'.format(data['event'])
        message = {
            'order_id': data['order_id'],
            'phones': (data['phone1'], ),
        }
        print(event, message)
        await cls.publish(event, message, app)


@lru_cache(maxsize=100)
def select_handlers(event):
    return [cls.handle for cls in BaseHandler.__subclasses__() if event.upper() in cls.EVENTS]
