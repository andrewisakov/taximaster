from .base import BaseEvent


class DriverOperCreate(BaseEvent):
    EVENT = 'DRIVER:OPER_CREATE'

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)


class DriverOperCreated(BaseEvent):
    EVENT = 'DRIVER:OPER_CREATED'


class DriverOperUpdated(BaseEvent):
    EVENT = 'DRIVER:OPER_UPDATED'
