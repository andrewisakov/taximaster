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
        cls.LOGGER.debug('Got new data: %s', str(data))
        term_account = data['account']
        term_id = data['txn_id']
        oper_sum = data['amount']
        oper_type = ['receipt', 'expense'][data['oper_type']]
        trm_id = data['trm_id']
        term_summ = data['from_amount']
        # comment = data['comment']
        opertime = data['DATE']

        async with cls.PG_POOL.acquire() as pgcon:
            async with pgcon.cursor() as c:
                await c.execute((
                    'select term_prefix, id from pay_systems;'
                ))
                pay_systems = {ps[0]: ps[1] for ps in (await c.fetchall())}

                await c.execute((
                    'select id from driver_oper where term_id=%(term_id)s and coalesce(deleted, 0) = 0;'
                ), {'term_id': term_id})
                oper_id = await c.fetchone()
                if oper_id:
                    cls.LOGGER.warning('Duplicate operation %s!', oper_id)
                    data.update(oper_id=oper_id)
                    duplicate = DriverOperDuplicate(data)
                    await duplicate.publish()
                    return

                await c.execute((
                    'select id '
                    'from drivers '
                    'where term_account is not null '
                    'and term_account = %(term_account)s;'
                ), {'term_account': term_account})

                driver_id = await c.fetchone()
                if not driver_id:
                    await c.execute((
                        'select id '
                        'from drivers '
                        'where term_account is not null '
                        'and term_account = %s(term_account)s;'
                    ), {'term_account': '00000'})
                    driver_id = await c.fetchone()
                    data['comment'] = f'Недопустимый аккаунт {term_account}!'
                    cls.LOGGER.warning(
                        'Term account %s is not exists!', term_account)

        data = {'driver_id': driver_id[0],
                'oper_sum': float(data['amount']),
                'oper_type': ['receipt', 'expense'][data['oper_type']],
                'comment': data.get('comment')
                }

        operation = await TMAPI.create_driver_operation(data)
        oper_id = operation.get('data', {}).get('oper_id')
        if not oper_id:
            cls.LOGGER.error(
                'Operation is not created! Data: %s', str(operation))
            return

        data['oper_id'] = oper_id
        cls.LOGGER.debug('Operation %s created.', oper_id)
        created = DriverOperCreated(data)
        await created.publish()
        UPDATE = ((
            'update driver_oper set term_operation=1, '
            'term_id = %(term_id)s, '
            'term_opertime=%(opertime)s, '
            'term_pay_system_id=%(pay_system)s, '
            'term_summ=%(term_summ)s, '
            'comment=%(comment)s '
            'where id=%(oper_id)s;'
        ), {
            'term_id': term_id,
            'opertime': opertime,
            'pay_system': pay_systems.get(trm_id, 0),
            'term_summ': term_summ,
            'comment': data.get('comment'),
            'oper_id': oper_id,
        })
        async with cls.PG_POOL.acquire() as pgcon:
            async with pgcon.cursor() as c:
                try:
                    await c.execute(UPDATE[0], UPDATE[1])
                    data['code'] = 0
                    updated = DriverOperUpdated(data)
                    await updated.publish()
                except Exception as e:
                    pgcon.rollback()
                    data['code'] = -1
                    date['exc'] = str(e)
                    oper_error = DriverOperError(data)
                    await oper_error.publish()
        cls.LOGGER.debug('Operation %s successfully updated.', oper_id)
