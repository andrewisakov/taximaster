from .base import BaseEvent


class OrderChangeState(BaseEvent):
    EVENT = 'ORDER:CHANGE_STATE'

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)


class OrderSetCreated(BaseEvent):
    EVENT = 'ORDER:SET_CREATED'

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)


class OrderNoCarsAborted(BaseEvent):
    EVENT = 'ORDER:SET_NO_CARS_ABORTED'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
