from .base import BaseEvent


class CallbackOriginateMixin:
    CALL_STATE = None

    @classmethod
    async def set_call_state(cls, data):
        if isinstance(cls.CALL_STATE, int):
            await TMAPI.set_request_state(
                {'order_id': data['order_id'],
                 'state': cls.CALL_STATE,
                 'phone_type': 1,
                 'state_id': 0,
                 },)


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


class CallbackOriginateBusy(CallbackOriginateMixin, BaseEvent):
    EVENT = 'CALLBACK:ORIGINATE:BUSY'
    CALL_STATE = 3

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        await cls.set_call_state(data)


class CallbackOriginateNoanswer(CallbackOriginateMixin, BaseEvent):
    EVENT = 'CALLBACK:ORIGINATE:NOANSWER'
    CALL_STATE = 4

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        await cls.set_call_state(data)


class CallbackOriginateError(CallbackOriginateMixin, BaseEvent):
    EVENT = 'CALLBACK:ORIGINATE:ERROR'
    CALL_STATE = 4

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        await cls.set_call_state(data)


class CallbackOriginateUnknownError(CallbackOriginateError):
    EVENT = 'CALLBACK:ORIGINATE:UNKNOWN_ERROR'
