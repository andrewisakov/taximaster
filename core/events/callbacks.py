from .base import BaseEvent
from ..coreapi import TMAPI


class CallbackOriginateMixin:
    CALL_STATE = None
    CALLBACK_STOP = []
    CALLBACK_START = []

    @classmethod
    async def block_last_event(cls, data):
        order_id = data.get('order_id')
        async with cls.PG_POOL.acquire() as pgcon:
            async with pgcon.cursor() as c:
                await c.execute(
                    ('select event from order_events '
                     'where order_id=%(order_id)s '
                     'order by timestamp desc limit 1;'),
                    order_id)
                last_event = await c.fetchone()
                return last_event in cls.CALLBACK_STOP

    @classmethod
    async def set_call_state(cls, data):
        if isinstance(cls.CALL_STATE, int):
            return await TMAPI.set_request_state(
                {'order_id': data['order_id'],
                 'state': cls.CALL_STATE,
                 'phone_type': 1,
                 'state_id': 0,
                 },
            )


class CallbackOriginateAccepted(CallbackOriginateMixin, BaseEvent):
    EVENT = 'CALLBACK:ORIGINATE:ACCEPTED'
    CALL_STATE = 0

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        await cls.set_call_state(data)


class CallbackOriginateStarted(CallbackOriginateMixin, BaseEvent):
    EVENT = 'CALLBACK:ORIGINATE:STARTED'
    CALL_STATE = 1

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        await cls.set_call_state(data)


class CallbackOriginateDelivered(CallbackOriginateMixin, BaseEvent):
    EVENT = 'CALLBACK:ORIGINATE:DELIVERED'
    CALL_STATE = 2

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        await cls.set_call_state(data)


class CallbackOriginateStart(BaseEvent):
    _EVENT = 'CALLBACK:ORIGINATE:START'

    async def publish(self):
        with await self._red_pool as redcon:
            await redcon.publish(self._EVENT, self.payload)


class CallbackOriginateBusy(CallbackOriginateMixin, BaseEvent):
    EVENT = 'CALLBACK:ORIGINATE:BUSY'
    CALL_STATE = 3
    BLOCKS = []

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        await cls.set_call_state(data)
        if not (await cls.block_last_event(data)):
            callback = CallbackOriginateStart(data)
            callback.publish()


class CallbackOriginateNoanswer(CallbackOriginateMixin, BaseEvent):
    EVENT = 'CALLBACK:ORIGINATE:NOANSWER'
    CALL_STATE = 4
    BLOCKS = []

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        await cls.set_call_state(data)
        if not (await cls.block_last_event(data)):
            callback = CallbackOriginateStart(data)
            callback.publish()


class CallbackOriginateError(CallbackOriginateMixin, BaseEvent):
    EVENT = 'CALLBACK:ORIGINATE:ERROR'
    CALL_STATE = 4
    BLOCKS = []

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        await cls.set_call_state(data)
        if not (await cls.block_last_event(data)):
            callback = CallbackOriginateStart(data)
            callback.publish()


class CallbackOriginateUnknownError(CallbackOriginateError):
    EVENT = 'CALLBACK:ORIGINATE:UNKNOWN_ERROR'


class CallbackOriginateNoRoute(BaseEvent):
    EVENT = 'CALLBACK:ORIGINATE:NO_ROUTE'


class CallbackOriginateNoDistributor(CallbackOriginateNoRoute):
    EVENT = 'CALLBACK:ORIGINATE:NO_DISTRIBUTOR'
    

class CallbackOriginateConnectError(BaseEvent):
    EVENT = 'CALLBACK:ORIGINATE:CONNECT_ERROR'


class CallbackOriginateInvalidGateway(BaseEvent):
    EVENT = 'CALLBACK:ORIGINATE:INVALID_GATEWAY'


class CallbackOriginateNormalTemporaryFailure(BaseEvent):
    EVENT = 'CALLBACK:ORIGINATE:NORMAL_TEMPORARY_FAILURE'
