import datetime
from collections import deque
from core.utils.json import get_value


def get_distributor(phone, db):

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

    date_time = datetime.datetime.utcnow()
    date_time = datetime.datetime(
        date_time.year, date_time.month, date_time.day, 0, 0, 0)
    ARGS = (date_time, phone[:3], int(phone[3:]), )

    c = db.cursor()
    c.execute(SELECT, ARGS)
    try:
        sim_id, address, channel, _, distributor, _ = c.fetchone()
        channel %= 5060
    except Exception as e:
        # logger.warning('get_distributor exception 1: %s %s' % (e, phone))
        sim_id, address, channel, _, distributor, _ = None, '', 0, 0, None, False
    c.close()
    # logger.debug('%s %s %s %s %s' %
    #              (phone, distributor, address, channel, sim_id))
    # db.close()
    return sim_id, address, channel, distributor
