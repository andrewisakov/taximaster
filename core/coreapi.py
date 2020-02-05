import hashlib
import datetime
import inspect
import json
import urllib.parse

import aiohttp
import xmltodict

from core.utils.json import get_value


class TMAPIBase:
    TM_HOST = None
    TM_PORT = None
    TM_SOLT = None
    PG_POOL = None
    ASTERISK_SOUNDS = None
    CONTENT_TYPE_X_WWW_FORM_URLENCODED = 'application/x-www-form-urlencoded'
    CONTENT_TYPE_APP_JSON = 'application/json'
    INLINE_SIGN = ['set_request_state',
                   'get_info_by_order_id',
                   'change_order_state']

    @classmethod
    async def _request(cls, method, url, headers, data=None, json=None):
        method = method.lower()
        response = None

        async with aiohttp.ClientSession(headers=headers, connector=aiohttp.TCPConnector(ssl=False)) as session:
            method = getattr(session, method)
            async with method(url, data=data, json=json) as r:
                response = r
                response = await response.text()
        return response

    @classmethod
    def _signature(cls, data):
        return hashlib.md5((data+cls.TM_SOLT).encode()).hexdigest()

    @classmethod
    async def _inline_request(cls, api, ver, data, request, method='GET'):
        method = method.upper()
        url = f'https://{cls.TM_HOST}:{cls.TM_PORT}/{api}/{ver}/{request}'
        params = urllib.parse.urlencode(data)
        _signature = cls._signature(params)

        headers = {'Signature': _signature,
                   'Content-Type': cls.CONTENT_TYPE_X_WWW_FORM_URLENCODED,
                   }

        if request in cls.INLINE_SIGN:
            params += f'&signature={_signature}'

        if method == 'GET':
            if request in cls.INLINE_SIGN:
                url += f'?{params}'
            params = None

        response = await cls._request(method, url, headers, data=params)

        try:
            # JSON ?
            response = json.loads(response)
        except Exception as e:
            try:
                # XML ?
                response = json.loads(
                    json.dumps(
                        xmltodict.parse(response)
                    )
                )
                response = response.get('response')
            except Exception as e:
                response = response

        for r in response.get('data', {}):  # Конвертация 'ГГГГММДДЧЧММСС' в datetime
            try:
                if len(response['data'].get(r, '')) == 14:
                    response['data'][r] = datetime.datetime.strptime(
                        response['data'][r], '%Y%m%d%H%M%S')
            except Exception as e:
                pass

        return response

    @classmethod
    async def _json_request(cls, api, ver, data, request, method='POST'):
        url = f'https://{cls.TM_HOST}:{cls.TM_PORT}/{api}/{ver}/{request}'
        headers = {'Signature': cls._signature(json.dumps(data)),
                   'Content-Type': cls.CONTENT_TYPE_APP_JSON,
                   }
        response = await cls._request(method.lower(), url, headers, json=data)
        return response


class TMAPI(TMAPIBase):
    @classmethod
    async def set_request_state(cls, data, *args, **kwargs):
        return await cls._inline_request('tm_tapi', '1.0', data,
                                         request='set_request_state', method='POST')

    @classmethod
    async def create_driver_operation(cls, data, *args, **kwargs):
        return await cls._json_request('common_api', '1.0', data,
                                       request='create_driver_operation', method='POST')

    @classmethod
    async def save_client_feed_back(cls, data, *args, **kwargs):
        return await self._json_request('common_api', '1.0', data,
                                        request='save_client_feed_back', method='POST')

    @classmethod
    async def ping(cls, data, *args, **kwargs):
        return await cls._inline_request('common_api', '1.0', data,
                                         request='ping', method='GET')

    @classmethod
    async def get_finished_orders(cls, data, *args, **kwargs):
        return await cls._inline_request('common_api', '1.0', data,
                                         request='get_finished_orders', method='GET')

    @classmethod
    async def get_drivers_info(cls, data, *args, **kwargs):
        return await cls._inline_request('common_api', '1.0', data,
                                         request='get_drivers_info', method='GET')

    @classmethod
    async def get_driver_info(cls, data, *args, **kwargs):
        return await cls._inline_request('common_api', '1.0', data,
                                         request='get_driver_info', method='GET')

    @classmethod
    async def get_order_state(cls, data, *args, **kwargs):
        return await cls._inline_request('common_api', '1.0', {'order_id': data.get('order_id')},
                                         request='get_order_state', method='GET')

    @classmethod
    async def check_authorization(cls, data, *args, **kwargs):
        return await cls._inline_request('common_api', '1.0', data,
                                         request='check_authorization', method='GET')

    @classmethod
    async def get_car_info(cls, data, *args, **kwargs):
        return await cls._inline_request('common_api', '1.0', data,
                                         request='get_car_info', method='GET')

    @classmethod
    async def get_crew_groups_list(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._inline_request('common_api', '1.0', data,
                                         request=request, method='GET')

    @classmethod
    async def get_crews_info(cls, data, *args, **kwargs):
        return await cls._inline_request('common_api', '1.0', data,
                                         request='get_crew_groups_list', method='GET')

    @classmethod
    async def get_tariffs_list(cls, data, *args, **kwargs):
        return await cls._inline_request('common_api', '1.0', data,
                                         request='get_tariffs_list', method='GET')

    @classmethod
    async def get_services_list(cls, data, *args, **kwargs):
        return await cls._inline_request('common_api', '1.0', data,
                                         request='get_services_list', method='GET')

    @classmethod
    async def get_discounts_list(cls, data, *args, **kwargs):
        return await cls._inline_request('common_api', '1.0', data,
                                         request='get_discounts_list', method='GET')

    @classmethod
    async def get_current_orders(cls, data, *args, **kwargs):
        return await cls._inline_request('common_api', '1.0', data,
                                         request='get_current_orders', method='GET')

    @classmethod
    async def get_info_by_order_id(cls, data, *args, **kwargs):
        return await cls._inline_request('tm_tapi', '1.0', data,
                                         request='get_info_by_order_id', method='GET')

    @classmethod
    async def change_order_state(cls, data, *args, **kwargs):
        return await cls._inline_request('tm_tapi', '1.0', data,
                                         request='change_order_state', method='POST')

    @classmethod
    async def create_order2(cls, data, *args, **kwargs):
        return await cls._json_request('common_api', '1.0', data,
                                       request='create_order2', method='POST')

    @classmethod
    async def get_order_state_id(cls, state_name, *args, **kwargs):
        with await cls.PG_POOL.acquire() as pgcon:
            with await pgcon.cursor() as c:
                await c.execute('select settings, id from order_states where is not null;')
                async for r in c:
                    sets = xmltodict.parse(r[0])
                    if int(get_value('settings.oktell.to_client.use_call_back', sets)):
                        event_name = get_value(
                            'settings.oktell.to_client.script_name', sets).upper()
                    if event_name == state_name:
                        return r[1]

    @classmethod
    async def create_message(cls, event, data):
        if not cls.ASTERISK_SOUNDS:
            cls.LOGGER.error('Отсутсвует описание озвучки!')
            return [], None

        message = cls.ASTERISK_SOUNDS.get(event, cls.ASTERISK_SOUNDS.MESSAGE_TYPE)
        if not message:
            cls.LOGGER.error('Отсутствует озвучка для события %s!', event)
            return [], None

        if event == 'ORDER_NO_CARS':
            return [f'{message}.wav'], None 
        
        sms_message = ''

        mark = data.get('car_mark', '').strip()
        model = data.get('car_model', '').strip()
        color = data.get('car_color', '').strip()
        gosn = data.get('gosnumber', '').strip()
        source_time = data.get('source_time')
        car_id = data.get('car_id',)
        driver_timecount = int(data.get('driver_timecount', 0))
        discountedsumm = data.get('discountedsumm')
        cashless = data.get('client_id', 0) != 0

        mark = mark.split(' ')[0]
        mark_sound = cls.ASTERISK_SOUNDS.get(mark, cls.ASTERISK_SOUNDS.MARK_TYPE)
        if not mark_sound:
            cls.LOGGER.warning('Отсутсвует озвучка для "%s"!', mark)
        sms_message += f'{mark}'
        
        model_sound = []
        if mark.upper().split(' ')[0] == 'ВАЗ':
            sms_message += f' {model}\n'
            ma = {0: model[:2], 2: model[-2:]}
            if len(model) == 5:
                ma[1] = model[2]
            for m in sorted(ma):
                if len(ma[m]) == 2:
                    if ma[m][0] == '1':
                        model_sound.append(f'tm{ma[m]}')
                    elif ma[m][0] == '0':
                        model_sound.append('tm{ma[m][0]}')
                        model_sound.append('tm{ma[m][1]}')
                    else:
                        model_sound.append('tm{ma[m][0]}0')
                        model_sound.append('tm{ma[m][1]}')
                else:
                    model_sound.append(f'tm{ma[m]}')
        else:
            sms_message += '\n'
        model_sound = '&'.join(model_sound)

        color_sound = ''
        if color:
            color_sound = cls.ASTERISK_SOUNDS.get(color, cls.ASTERISK_SOUNDS.COLOR_TYPE)
            sms_message += f'{color}\n'
        if not color_sound:
            cls.LOGGING.warning('Отсутствует озвучка для "%s"!', color)
            message = message.replace('&tmColor', '')
        
        gosn_sound = []
        if gosn:
            sms_message += f'{gosn}\n'
            gosn = (gosn[:len(gosn) - 2], gosn[-2:])
            for gn in gosn:
                if len(gn) == 1: # 100
                    gosn_sound.append(f'tm{gn}00')
                else:
                    if gn[0] == '1': # 10..19
                        gosn_sound.append(f'tm{gn}')
                    elif gn[0] == '0': # 0..9
                        if len(gosn) == 3 and gn[1] != '0':
                            gosn_sound.append(f'tm{gn[1]}')
                        else:
                            gosn_sound.append('tm0')
                            gosn_sound.append(f'tm{gn[1]}')
                    else:
                        gosn_sound.append(f'tm{gn[0]}0')
                        gosn_sound.append(f'tm{gn[1]}')
        else:
            cls.LOGGER.warinig('Отсутсвует госномер для car_id: %s', car_id)
            message = message.replace('&tmgos_nomer', '')
        gosn_sound = '&'.join(gosn_sound)
        
        minutes_timecount = []
        if driver_timecount and driver_timecount > 0:
            sms_message += f'{driver_timecount} мин\n'
            t = driver_timecount % 10
            d = driver_timecount // 10
            if driver_timecount > 19:
                minutes_timecount.append(f'tm{d}0')
                if t > 0:
                    minutes_timecount.append(f'tm{t}')
            else:
                minutes_timecount.append(f'tm{driver_timecount}')
        else:
            sms_message += '5-7 мин\n'
            minutes_timecount.append('tm5')
            minutes_timecount.append('tm7')
        
        minutes_timecount = '&'.join(minutes_timecount)

        message = message.replace('$mark', mark_sound)\
                        .replace('$model', model_sound)\
                        .replace('$color', color_sound)\
                        .replace('$gosnumber', gosn_sound)\
                        .replace('$minutes', minutes_timecount)\
                        .replace('&&', '&')\
                        .split('&')
        message = [f'{m}.wav' for m in message if m]
        sms_message += 'Расчёт по таксометру.'
        cls.LOGGER.info('SMS: %s', sms_message)
        cls.LOGGER.info('CALL:%s', message)
        return message, sms_message
