import asyncio
from imapclient import IMAPClient
import datetime
from core.events.drivers import DriverOperCreate
from .parsers import parse_body, parse_header
from .config import LEGAL_SENDERS


GATHER_POOL_SIZE = 8


async def save(message):
    if message['FROM'] not in LEGAL_SENDERS:
        return {}
    return message


async def check_mailbox(imap,
                        date_since=None,
                        from_id=None):

    date_since = date_since or datetime.datetime.now().date()
    if not from_id:
        y, m, d = str(date_since).split('-')
        m = date_since.strftime('%b')
        date_since = '-'.join([d, m, y])
        since = f'SINCE {date_since}'
    else:
        since = f'UID {from_id+1}:*'
    ids = imap.search(since)

    return ids


async def get_message(imap, msg_id, logger):
    header = imap.fetch([msg_id], 'BODY[header]')
    body = imap.fetch([msg_id], 'BODY[text]')
    if header and body:
        header = parse_header(header[msg_id][b'BODY[HEADER]'])
        body = parse_body(body[msg_id][b'BODY[TEXT]'])
        if header['FROM'] in LEGAL_SENDERS:
            oper_create = DriverOperCreate(payload=dict(**header, **body))
            await oper_create.publish()
            return msg_id
        else:
            logger.warning('Message %s from not legal senders!', str(header))


async def mail_stream(host, port, user, password, inbox, loop, logger):
    from_id = None
    with IMAPClient(host, port) as imap:
        resp = imap.login(user, password)
        if '(Success)' not in resp.decode():
            logger.error('Not logged: %s', resp)
            raise

        logger.debug('Logged: %s', resp)
        imap.select_folder(inbox, readonly=True)
        while 1:
            ids = await check_mailbox(imap, from_id=from_id)
            messages = [get_message(imap, i, logger=logger)
                        for i in ids if i > (from_id if from_id else 0)]

            if not messages:
                logger.debug('New messages not exists. Waiting...')
                await asyncio.sleep(60)
                continue

            for i in range(len(messages) // GATHER_POOL_SIZE + 1):
                result = await asyncio.gather(*messages[i*GATHER_POOL_SIZE:(i+1)*GATHER_POOL_SIZE])
                from_id = max([r for r in result if r] +
                              [0 if not from_id else from_id])
            logger.debug('Next message_id: %s+', from_id)
