from core.coreapi import TMAPI
from core.events.base import register, unregister
from core.events.callbacks import (CallbackOriginateBusy,
                                   CallbackOriginateDelivered,
                                   CallbackOriginateError,
                                   CallbackOriginateNoanswer,
                                   CallbackOriginateStarted,
                                   CallbackOriginateUnknownError)
from core.events.oktell import (
    OktellOrderAborted,
    OktellOrderAccepted,
    OktellOrderClientFuck,
    OktellOrderClientGone,
    OktellOrderClientInCar,
    OktellOrderCompleted,
    OktellOrderCrewAtPlace,
    OktellOrderNoCars
)

from .database import AsteriskSounds
