#!/usr/bin/python3
# verssion 2.1
import urllib.request
import urllib.error
import urllib.parse
import time
import json
import xmltodict
from collections import deque


SMS_LIST_INTERVAL = 10
TIMEOUT = 20
FROM = 'Народное'


class Channel:
    LOGGER = None
    auth_handler = urllib.request.HTTPDigestAuthHandler()

    def __init__(self, address, channel, login='user', passwd='user', realm='kts_voip', timeout=TIMEOUT):
        self._address = address
        self._login = login
        self._passwd = passwd
        self._realm = realm
        self._timeout = timeout
        self._channel = channel

    def __repr__(self):
        return f'{self._address}:{self._channel}'

    @property
    def url(self, cmd):
        return 'http://%s/%s' % (self._address, cmd)

    def request(self, cmd, data=None):
        self.auth_handler.add_password(
            realm=self._realm, uri=self.url(cmd), user=self._login, passwd=self._passwd)
        data = urllib.parse.urlencode(data).encode('utf-8') if data else data
        self.LOGGER.debug('Request %s for %s.', self.url(cmd), data)
        opener = urllib.request.build_opener(self.auth_handler)
        urllib.request.install_opener(opener)
        r = urllib.request.Request(self.url(cmd))
        try:
            o = urllib.request.urlopen(r, data, timeout=self._timeout)
            result = urllib.parse.unquote(o.read().decode('utf-8'))
            self.LOGGER.debug('Response %s from %s', result, self.url(cmd))
        except Exception as e:
            result = "{'message': 'error', 'error': '%s', 'address': %s}" % (
                e, self._address)
            self.LOGGER.error('Response %s from %s', result, self.url(cmd))

        return result

    # def config(self, channel):
    #     channel_config = self.request(
    #         self._address, f'json?a=getchconf&ch={channel}')
    #     channel_config = json.loads(channel_config)
    #     if channel_config.get('message') == 'ok':
    #         channel_config = channel_config.get('cfg', {})
    #     else:
    #         channel_config = {}
    #     return channel_config

    def get_smslist(self):
        self.set_time()
        self.LOGGER.debug('Get SMS list from %s.', self._address)
        smslist = self.request(cmd='json?a=smslist')
        try:
            smslist = json.loads(smslist)
            smslist = smslist.get('sms', [])
        except Exception as e:
            smslist = []
        self.LOGGER.debug('Got %s SMS from %s', len(smslist), self._address)
        return smslist

    def set_time(self, ts=time.time()):
        self.request(cmd='index?a=settime', data={
            'ts': str(int(ts))})
        return 0

    def send_sms(self, phone, message, is_flush=False):
        self.LOGGER.debug('Send SMS %s:%s throw %s', phone, message, self._address)
        time_ = time.time()
        result = self.request(cmd='sendsms',
                              data={
                                  'from': FROM,
                                  'ch': self._channel,
                                  'is_flush': 1 if is_flush else 0,
                                  'phone': phone,
                                  'text': message,
                              })
        return result

    def del_sms(self, sms_id=None):
        if sms_id:
            result = self.request(cmd='xml?a=delsms&id={sms_id}')
        else:
            result = self.request(cmd='xml?a=delallsms')

        try:
            result = xmltodict.parse(result)
            result = int(result.get('result', 1))
        except Exception as e:
            result = 0

        return result


class Channels:
    LOGGER = None

    def __init__(self, pg_pool, logger):
        self._channels = {}
        self._pg_pool = pg_pool
        self.LOGGER = logger

    def __repr__(self):
        _channels = ''
        for cs in self._channels.keys():
            _channels += ',%s: (%s)' % (cs, ','.join(self._channels[cs]))
        return _channels[1:]

    def get_distributor(self, phone):
        return 'inter_city'

    def register(self, channel: Channel, distributor=None):
        if distributor not in self._channels:
            self.LOGGER.debug(
                'Distributor %s not found. Created', distributor)
            self._channels[distributor] = deque()
        if channel not in self._channels[distributor]:
            channel.LOGGER = self.LOGGER
            self._channels[distributor].append(channel)
            self.LOGGER.debug('Channel %s registered.', channel)

    def unregister(self, channel: Channel):
        for d in self._channels.keys():
            self._channels[d].discard(channel)
            self.LOGGER.debug('Channel %s unregistered.', channel)

    def send_sms(self, message, phone):
        distributor = self.get_distributor(phone)
        self.LOGGER.debug('Sending SMS %s:%s throw %s.', phone, message, distributor)
        channel = self._channels[distributor].popleft()
        result = channel.send_sms(phone, message)
        self._channels[distributor].append(channel)
        self.LOGGER.debug(
            'Send SMS %s:%s result %s', phone, message, result)
        return result

    # @classmethod
    # def get_channels(cls, address):
    #     channels = request(address, 'json?a=chlist')
    #     channels = json.loads(channels)
    #     if channels['message'] == 'ok':
    #         channels = {int(ch['num']):
    #                     {'enabled': ch['enabled'] == 1,
    #                     'creg': 'REGISTERED' in ch['creg'].upper(),
    #                     'operator': ch['op'],
    #                     'present': ch['present'] == 1}
    #                     for ch in channels['channel']}
    #         channels['message'] = 'ok'
    #     return channels
