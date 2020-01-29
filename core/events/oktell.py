from .base import BaseEvent


class OktellMessageMixin:
    @classmethod
    async def create_message(cls, data):
        pass


class OktellOrderCreated(BaseEvent):
    EVENT = 'OKTELL:ORDER_CREATED'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        await super().handle(data)


class OktellOrderCompleted(BaseEvent):
    EVENT = 'OKTELL:ORDER_COMPLETED'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        await super().handle(data)


class OktellOrderAborted(BaseEvent):
    EVENT = 'OKTELL:ORDER_ABORTED'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)


class OktellOrderNoCars(OktellMessageMixin, BaseEvent):
    EVENT = 'OKTELL:ORDER_NO_CARS'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        data.update(**cls.create_message(data))


class OktellOrderAccepted(OktellMessageMixin, BaseEvent):
    EVENT = 'OKTELL:ORDER_ACCEPTED'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        data.update(**cls.create_message(data))


class OktellOrderCrewAtPlace(OktellMessageMixin, BaseEvent):
    EVENT = 'OKTELL:ORDER_CREW_AT_PLACE'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        data.update(**cls.create_message(data))


class OktellOrderClientInCar(BaseEvent):
    EVENT = 'OKTELL:ORDER_CLIENT_IN_CAR'

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)


class OktellOrderClientFuck(BaseEvent):
    EVENT = 'OKTELL:ORDER_CLIENT_FUCK'

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)


class OktellOrderClientGone(OktellMessageMixin, BaseEvent):
    EVENT = 'OKTELL:ORDER_CLIENT_GONE'

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        data.update(**cls.create_message(data))
