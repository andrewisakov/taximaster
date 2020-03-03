from ..coreapi import TMAPI
from .base import BaseEvent
from .orders import OrderSetCreated, OrderNoCarsAborted
from .callbacks import (
    CallbackOriginateBusy, CallbackOriginateDelivered,
    CallbackOriginateError, CallbackOriginateNoanswer,
    CallbackOriginateUnknownError, CallbackOriginateStart,
)


class OktellMessageMixin:
    @classmethod
    def create_message(cls, data):
        return TMAPI.create_message(cls.EVENT.split(':')[1], data)


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
        data['choice'] = {1: OrderSetCreated.EVENT,
                          6: OrderNoCarsAborted.EVENT}
        data['timeout'] = 5000
        data['tries'] = 3
        data.update(**cls.create_message(data))
        await cls.save(data)
        originate_start = CallbackOriginateStart(data, cls.RED_POOL)
        await originate_start.publish()


class OktellOrderAccepted(OktellMessageMixin, BaseEvent):
    EVENT = 'OKTELL:ORDER_ACCEPTED'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        data.update(**cls.create_message(data))
        await cls.save(data)
        originate_start = CallbackOriginateStart(data, cls.RED_POOL)
        await originate_start.publish()


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
