import datetime
import hashlib
import inspect
import json
import urllib.parse
import ssl

import aiohttp
import aiopg

import xmltodict

from core.utils.json import get_value


class TMAPIBase:
    TM_HOST = None
    TM_PORT = None
    TM_SOLT = None
    PG_POOL = None
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
