import datetime
import email
from dateutil.parser import parse


def parse_header(header):  # Разбор заголовка письма
    parser = email.parser.HeaderParser()
    header = parser.parsestr(header.decode())
    dd = parse(header.get('Date'))
    d = dd.date()
    t = dd.time()
    _date = datetime.datetime(
        d.year, d.month, d.day, t.hour, t.minute, t.second) - dd.tzinfo._offset
    _from = header['From']
    return {'DATE': str(_date), 'FROM': _from}


def parse_body(body):  # Разбор тела письма
    body = body.decode()
    body = body.replace('\r\n', '').replace('=3D', '=').split('=0D=0A')
    body = {cc[0]: cc[1] for cc in [cc.split('=') for cc in body]}
    body['account'] = body['account'].zfill(5)
    body['oper_type'] = 0
    body['comment'] = 'Пополнение баланса '
    return body
