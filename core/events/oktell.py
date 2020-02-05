from .base import BaseEvent
from ..coreapi import TMAPI


class OktellMessageMixin:
    @classmethod
    async def create_message(cls, data):
        return (await TMAPI.create_message(cls.EVENT.split(':')[1], data))


class OktellOrderCreated(BaseEvent):
    EVENT = 'OKTELL:ORDER_CREATED'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        await super().handle(data)
        await cls.save(data)


class OktellOrderCompleted(BaseEvent):
    EVENT = 'OKTELL:ORDER_COMPLETED'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        await super().handle(data)
        await cls.save(data)


class OktellOrderAborted(BaseEvent):
    EVENT = 'OKTELL:ORDER_ABORTED'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        await cls.save(data)


class OktellOrderNoCars(OktellMessageMixin, BaseEvent):
    EVENT = 'OKTELL:ORDER_NO_CARS'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        data.update(**cls.create_message(data))
        await cls.save(data)


class OktellOrderAccepted(OktellMessageMixin, BaseEvent):
    EVENT = 'OKTELL:ORDER_ACCEPTED'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        message_data = (await cls.create_message(data))
        data.update(**{'message': message_data[0], 'sms': message_data[1]})
        await cls.save(data)


class OktellOrderCrewAtPlace(OktellMessageMixin, BaseEvent):
    EVENT = 'OKTELL:ORDER_CREW_AT_PLACE'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        data.update(**cls.create_message(data))
        await cls.save(data)


class OktellOrderClientInCar(BaseEvent):
    EVENT = 'OKTELL:ORDER_CLIENT_IN_CAR'

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        await cls.save(data)


class OktellOrderClientFuck(BaseEvent):
    EVENT = 'OKTELL:ORDER_CLIENT_FUCK'

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        await cls.save(data)


class OktellOrderClientGone(OktellMessageMixin, BaseEvent):
    EVENT = 'OKTELL:ORDER_CLIENT_GONE'

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        data.update(**cls.create_message(data))
        await cls.save(data)
