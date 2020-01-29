from .base import BaseEvent


class DriverOperCreate(BaseEvent):
    EVENT = 'DRIVER:OPER_CREATE'

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
