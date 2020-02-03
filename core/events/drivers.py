from .base import BaseEvent
from ..coreapi import TMAPI


class DriverOperDuplicate(BaseEvent):
    EVENT = 'DRIVER:OPER:DUPLICATE'


class DriverOperCreated(BaseEvent):
    EVENT = 'DRIVER:OPER:CREATED'


class DriverOperUpdated(BaseEvent):
    EVENT = 'DRIVER:OPER:UPDATED'


class DriverOperError(BaseEvent):
    EVENT = 'DRIVER:OPER:ERROR'


class DriverOperCreate(BaseEvent):
    EVENT = 'DRIVER:OPER_CREATE'

    @classmethod
    async def handle(cls, data):
        data = await super().handle(data)

        term_account = data['BODY']['account']
        term_id = data['BODY']['txn_id']
        oper_sum = data['BODY']['amount']
        opert_type = ['receipt', 'expense'][data['oper_type']]
        async with cls.PG_POOL.acquire() as pgcon:
            async with pgcon.cursor() as c:
                await c.execute((
                    'select term_prefix, id from pay_systems;'
                ))
                pay_systems = {ps[0]: ps[1] for ps in (await c.fetchall())}

                await c.execute((
                    'select id from driver_oper where term=%(term_id)s and cast(deleted, 0) = 0;'
                ), {'term_id': term_id})
                oper_id = await c.fetchone()
                if oper_id:
                    data.update(oper_id=oper_id)
                    duplicate = await DriverOperDuplicate(data)
                    await duplicate.publish()
                    return

                await c.execute((
                    'select id '
                    'from drivers '
                    'where term_account is not null '
                    'and term_account = %s(term_account)s;'
                ), {'term_account': term_account})

                driver_id = await c.fetchall()
                if not driver_id:
                    await c.execute((
                        'select id '
                        'from drivers '
                        'where term_account is not null '
                        'and term_account = %s(term_account)s;'
                    ), {'term_account': '00000'})
                    driver_id = await c.fetchone()
                    data['comment'] = f'Недопустимый аккаунт {term_account}!'

        operation = await TMAPI.create_driver_operation(data)
        oper_id = operation.get('oper_id')
        if not oper_id:
            return

        data['oper_id'] = oper_id
        created = DriverOperCreated(data)
        created.publish()
        trm_id = data['BODY']['trm_id']
        term_summ = data['BODY']['from_amount']
        comment = data['comment']
        opertime = data['DATE']
        UPDATE = ((
            'update driver_oper set term_operation=1, '
            'term_id = %(term_id)s, '
            'term_opertime=%(opertime)s, '
            'term_pay_system_id=%(pay_system), '
            'term_summ=%(term_summ)s, '
            'comment=%(comment)s '
            'where id=%(oper_id)s;'
        ), {
            'term_id': term_id,
            'opertime': opertime,
            'pay_system': pay_systems.get(trm_id, 0),
            'term_summ': term_summ,
            'comment': comment,
            'oper_id': oper_id,
        })
        async with cls.PG_POOL.acquire() as pgcon:
            async with pgcon.cursor() as c:
                try:
                    await c.execute(UPDATE)
                    data['code'] = 0
                    updated = await DriverOperUpdated(data)
                    await updated.publish()
                except Exception as e:
                    data['code'] = -1
                    oper_error = DriverOperError(data)
                    oper_error.publish()
