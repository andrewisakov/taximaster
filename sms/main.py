import json
import redis
import threading
import logging
from psycopg2.pool import ThreadedConnectionPool
from core.events.oktell import OktellOrderAccepted
from core.coreapi import TMAPI
from .kts.channels import Channel, Channels
from .config import REDIS, CHANNELS, DSN, TME_DB
from orders.database import AsteriskSounds


LOGGER = logging.getLogger()


def enrich_data(data):
    with TMAPI.PG_POOL.getconn() as pgcon:
        with pgcon.cursor() as c:
            c.execute((
                'select o.driver_timecount, '
                'o.discountedsumm, o.clientid as client_id, '
                'o.driverid, o.cashless, o.state, o.phone, '
                'cr.gosnumber, cr.color as car_color, '
                'cr.mark as car_mark, coalesce(cr.model, \'\') as car_model, '
                'cr.id as car_id, o.source_time '
                'from orders o '
                'join crews cw on (cw.id=o.crewid) '
                'join cars cr on (cr.id=cw.carid) '
                'where o.id=%(order_id)s;'),
                {'order_id': data['order_id']})
            r = c.fetchone()
            if r:
                order_data = {cn.name :r[ix] for ix, cn in enumerate(c.description)}
                data.update(**order_data)
    return data

def get_distributor(phone, db):
    LOGGER.debug(phone)

    phone = phone[-10:]
    SELECT = 'select sc.id, d.address, c.port as channel, count(sms.*) as sim_count, dst.name, dst_sms.sms '\
             'from routes_mask roma '\
             'join regions reg on (reg.id=roma.region_id) '\
             'join operators op on (op.id=roma.operator_id) '\
             'join distributors dst on (dst.id=op.distributor_id or dst.id=0) '\
             'left join distributors dst_sms on (dst_sms.id=op.distributor_id) '\
             'join sim_cards sc on (sc.distributor_id=dst.id) '\
             'join channels c on (c.id=sc.channel_id) '\
             'join devices d on (d.id=c.device_id) '\
             'left join sms on (sms.sim_id=sc.id and sms.date_time > %s and sms.direction=1) '\
             'where (roma.aaa=%s and %s between roma.range_a and roma.range_b) and '\
             'sc.direction=2 and sc.is_active and (reg.is_home or dst.all_home) and '\
             '(dst_sms.sms or (dst_sms.id = dst.id)) '\
             'group by sc.id, d.address, c.port, dst.id, dst_sms.sms '\
             'order by dst.id desc, sim_count '\
             'limit 1;'

    date_time = datetime.datetime.now()
    date_time = datetime.datetime(
        date_time.year, date_time.month, date_time.day, 0, 0, 0)
    ARGS = (date_time, phone[:3], int(phone[3:]), )
    # logger.debug('get_distributor: %s %s' % (SELECT, ARGS))
    c = db.cursor()
    c.execute(SELECT, ARGS)
    try:
        sim_id, address, channel, _, distributor, _ = c.fetchone()
        channel %= 5060
    except Exception as e:
        LOGGER.warning('get_distributor exception 1: %s %s' % (e, phone))
        sim_id, address, channel, _, distributor, _ = None, '', 0, 0, None, False
    c.close()
    LOGGER.debug('%s %s %s %s %s' %
                 (phone, distributor, address, channel, sim_id))
    # db.close()
    return sim_id, address, channel, distributor


def register_channels(pg_pool):
    SELECT = (
        'select distinct d.address, c.port%5060 as port, dest.name '
        'from devices d '
        'join channels c on (c.device_id=d.id) '
        'join sim_cards sc on (sc.id=c.sim_id) '
        'join distributors dest on (dest.id=sc.distributor_id) '
        'where d.name like \'КТС%\' and c.is_active and sc.direction=2 '
        'order by d.address, port'
    )
    channels = Channels(pg_pool, LOGGER)
    with pg_pool.getconn() as pgconn:
        with pgconn.cursor() as c:
            c.execute(SELECT)

            [channels.register(Channel(address=ch[0], channel=ch[1]),
                               distributor=ch[-1]) for ch in c.fetchall()]
    return channels


def main():
    TMAPI.LOGGER = LOGGER
    TMAPI.ASTERISK_SOUNDS = AsteriskSounds()
    pg_pool = ThreadedConnectionPool(*DSN)
    TMAPI.PG_POOL = ThreadedConnectionPool(*TME_DB)
    channels = register_channels(pg_pool)
    redpool = redis.ConnectionPool(host=REDIS)
    r = redis.Redis(connection_pool=redpool)
    rs = r.pubsub()
    rs.subscribe(CHANNELS)

    for event in rs.listen():
        LOGGER.debug('Received %s', event)
        if event['type'] == 'message':
            LOGGER.debug('Got message: %s', event)
            channel = event['channel'].decode().split(':')[1]
            data = json.loads(event['data'])
            data = enrich_data(data)
            phones = data['phones'][0]
            data = TMAPI.create_message(channel, data)

            _channel = threading.Thread(
                target=channels.send_sms, args=(data['sms'], phones))
            _channel.start()
            LOGGER.debug('%s: %s', _channel, event)


if __name__ == '__main__':
    try:
        m = threading.Thread(target=main)
        m.start()
        m.join()
    except KeyboardInterrupt as e:
        exit(0)
