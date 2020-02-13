import datetime
import email
from decimal import Decimal
from dateutil.parser import parse


def parse_header(header):  # Разбор заголовка письма
    header = header[1][0][1].decode('UTF-8')
    parser = email.parser.HeaderParser()
    header = parser.parsestr(header)
    dd = parse(header.get('Date'))
    d = dd.date()
    t = dd.time()
    header['DATE'] = datetime.datetime(
        d.year, d.month, d.day, t.hour, t.mimute, t.second) - dd.tzinfo._offset
    header['FROM'] = header['From']
    return header['DATE'], header['FROM']


def parse_body(body):  # Разбор тела письма
    body = body[1]
    body = body.decode()
    body = body.replace('\r\n', '').replace('=3D', '=').split('=0D=0A')
    body = {cc[0]: cc[1] for cc in [cc.split('=') for cc in body]}
    body['from_amount'] = Decimal(body['from_amount'])
    body['amount'] = Decimal(body['amount'])
    body['account'] = body['account'].zfill(5)
    return body
