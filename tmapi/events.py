import asyncio
import json
from core import TMAPI


class BaseEvent:
    EVENT = None
    ENRICH_DATA = False
    LOGGER = None

    async def create(self, payload):
        self._payload = payload

    async def publish(self):
        with await self.REDCON.acquire() as redcon:
            redcon.publish(self.EVENT, self.payload)

    @property
    def payload(self):
        return json.dumps(self._payload)

    @classmethod
    async def handle(cls, data):
        data = await cls.tmapi_request(data)
        return data

    @classmethod
    async def channel_reader(cls, channel):
        while await channel.wait_message():
            message = await channel.get_json()
            cls.LOGGER.debug('Got %s: %s', channel.name, message)
            result = await cls.handle(message)

    @classmethod
    async def tmapi_request(cls, data):
        result = {}
        if cls.ENRICH_DATA:
            cls.LOGGER.debug('Enrich order %s data.', data['order_id'])
            order_state = TMAPI.get_order_state(data)
            order_info = TMAPI.get_info_by_order_id(
                {**data,
                 'fields': ('DRIVER_TIMECOUNT-'
                            'SUMM-'
                            'SUMCITY-'
                            'DISCOUNTEDSUMM-'
                            'SUMCOUNTRY-'
                            'SUMIDLETIME-'
                            'CASHLESS-'
                            'CLIENT_ID'),
                 })
            # Консолидидация результатов двух запросов. Кривизна TM API...
            result = order_state['data'].update(order_info['data'])
        return result


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
    EVENT = 'CALLBACK_ORIGINATE_ACCEPTED'
    CALL_STATE = 0

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        await cls.set_call_state(data)


class CallbackOriginateStarted(CallbackOriginateMixin, BaseEvent):
    EVENT = 'CALLBACK_ORIGINATE_STARTED'
    CALL_STATE = 1

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        await cls.set_call_state(data)


class CallbackOriginateDelivered(CallbackOriginateMixin, BaseEvent):
    EVENT = 'CALLBACK_ORIGINATE_DELIVERED'
    CALL_STATE = 2

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        await cls.set_call_state(data)


class CallbackOriginateBusy(CallbackOriginateMixin, BaseEvent):
    EVENT = 'CALLBACK_ORIGINATE_BUSY'
    CALL_STATE = 3

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        await cls.set_call_state(data)


class CallbackOriginateNoanswer(CallbackOriginateMixin, BaseEvent):
    EVENT = 'CALLBACK_ORIGINATE_NOANSWER'
    CALL_STATE = 4

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        await cls.set_call_state(data)


class CallbackOriginateError(CallbackOriginateMixin, BaseEvent):
    EVENT = 'CALLBACK_ORIGINATE_ERROR'
    CALL_STATE = 4

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        await cls.set_call_state(data)


class CallbackOriginateUnknownError(CallbackOriginateError):
    EVENT = 'CALLBACK_ORIGINATE_UNKNOWN_ERROR'


class OrderChangeState(BaseEvent):
    EVENT = 'ORDER_CHANGE_STATE'

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)


class OrderSetCreated(BaseEvent):
    EVENT = 'ORDER_SET_CREATED'

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)


class OrderNoCarsAborted(BaseEvent):
    EVENT = 'ORDER_SET_NO_CARS_ABORTED'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)


class DriverOperCreate(BaseEvent):
    EVENT = 'DRIVER_OPER_CREATE'

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)


class OktellMessageMixin:
    @classmethod
    async def create_message(cls, data):
        pass


class OktellOrderCreated(BaseEvent):
    EVENT = 'OKTELL_ORDER_CREATED'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        await super().handle(data)


class OktellOrderCompleted(BaseEvent):
    EVENT = 'OKTELL_ORDER_COMPLETED'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        await super().handle(data)


class OktellOrderAborted(BaseEvent):
    EVENT = 'OKTELL_ORDER_ABORTED'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)


class OktellOrderNoCars(OktellMessageMixin, BaseEvent):
    EVENT = 'OKTELL_ORDER_NO_CARS'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        data.update(**cls.create_message(data))


class OktellOrderAccepted(OktellMessageMixin, BaseEvent):
    EVENT = 'OKTELL_ORDER_ACCEPTED'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        data.update(**cls.create_message(data))


class OktellOrderCrewAtPlace(OktellMessageMixin, BaseEvent):
    EVENT = 'OKTELL_ORDER_CREW_AT_PLACE'
    ENRICH_DATA = True

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        data.update(**cls.create_message(data))


class OktellOrderClientInCar(BaseEvent):
    EVENT = 'OKTELL_ORDER_CLIENT_IN_CAR'

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)


class OktellOrderClientFuck(BaseEvent):
    EVENT = 'OKTELL_ORDER_CLIENT_FUCK'

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)


class OktellOrderClientGone(OktellMessageMixin, BaseEvent):
    EVENT = 'OKTELL_ORDER_CLIENT_GONE'

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)
        data.update(**cls.create_message(data))


async def register(loop, redcon, logger):
    channels = []
    for cls in BaseEvent.__subclasses__():
        if cls.EVENT:
            channel = await redcon.subscribe(cls.EVENT)
            channels.append(asyncio.ensure_future(
                cls.channel_reader(channel[0]), loop=loop))
            cls.LOGGER = logger
            cls.REDCON = redcon
            logger.debug('Event %s registered %s', cls.EVENT, channel)
    logger.debug('%s events registered.', len(channels))
    return channels


async def unregister(channels):
    await redcon.unsubscribe(*[ch for ch in channels.keys()])
