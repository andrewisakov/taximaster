import datetime
import hashlib
import inspect
import json
import urllib.parse

import aiohttp
import aiopg

import xmltodict

from settings import SAULT, SERVICE_ROOT_DIR, TM_HOST, TM_PORT, DSN
from core.utils.json import get_value


class TMAPIBase:
    CONTENT_TYPE_X_WWW_FORM_URLENCODED = 'application/x-www-form-urlencoded'
    CONTENT_TYPE_APP_JSON = 'application/json'
    INLINE_SIGN = ['set_request_state',
                   'get_info_by_order_id',
                   'change_order_state']

    @classmethod
    async def _request(cls, method, url, headers, data=None, json=None):
        method = method.lower()
        response = None
        context = ssl._create_unverified_context()

        async with aiohttp.ClientSession(headers=headers) as session:
            method = getattr(session, f'_{method.lower()}')
            async with method(url, data=data, json=json, ssl=context) as r:
                response = r
        return response

    @classmethod
    def _signature(self, data):
        return hashlib.md5((data+SAULT).encode()).hexdigest()

    @classmethod
    async def _inline_request(cls, api, ver, data, request, method='GET'):
        method = method.upper()
        url = f'https://{TM_HOST}:{TM_PORT}/{api}/{ver}/{request}'
        params = urllib.parse.urlencode(data)
        _signature = cls._signature(params)

        headers = {'Signature': _signature,
                   'Content-Type': cls.CONTENT_TYPE_X_WWW_FORM_URLENCODED,
                   }

        if request in cls.INLINE_SIGN:
            params += f'&signature={_signature}'

        if method == 'GET':
            url += f'?{params}'
            params = None

        response = await cls._request(method, url, headers, data=params)

        try:
            # JSON ?
            response = response.json()
        except Exception as e:
            try:
                # XML ?
                response = json.loads(
                    json.dumps(
                        xmltodict.parse(response)
                    )
                ).get('response')
            except Exception as e:
                response = response

        for r in response.get('data'):  # Конвертация 'ГГГГММДДЧЧММСС' в datetime
            try:
                if len(response['data'].get(r, '')) == 14:
                    response['data'][r] = datetime.datetime.strptime(
                        response['data'][r], '%Y%m%d%H%M%S')
            except Exception as e:
                pass

        return response

    @classmethod
    async def _json_request(cls, api, ver, data, request, method='POST'):
        url = f'https://{TM_HOST}:{TM_PORT}/{api}/{ver}/{request}'
        headers = {'Signature': cls._signature(data),
                   'Content-Type': cls.CONTENT_TYPE_APP_JSON,
                   }
        response = await cls._request(method.lower(), url, headers, json=data)
        return response


class TMAPI(TMAPIBase):
    @classmethod
    async def get_request_state(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._inline_request('tm_tapi', '1.0', data,
                                         request=request, method='POST')

    @classmethod
    async def create_driver_operation(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._json_request('common_api', '1.0', data,
                                       request=request, method='POST')

    @classmethod
    async def save_client_feed_back(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._json_request('common_api', '1.0', data,
                                        request=request, method='POST')

    @classmethod
    async def ping(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._inline_request('common_api', '1.0', data,
                                         request=request, method='GET')

    @classmethod
    async def get_finished_orders(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._inline_request('common_api', '1.0', data,
                                         request=request, method='GET')

    @classmethod
    async def get_drivers_info(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._inline_request('common_api', '1.0', data,
                                         request=request, method='GET')

    @classmethod
    async def get_driver_info(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._inline_request('common_api', '1.0', data,
                                         request=request, method='GET')

    @classmethod
    async def get_order_state(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._inline_request('common_api', '1.0', data,
                                         request=request, method='GET')

    @classmethod
    async def check_authorization(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._inline_request('common_api', '1.0', data,
                                         request=request, method='GET')

    @classmethod
    async def get_car_info(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._inline_request('common_api', '1.0', data,
                                         request=request, method='GET')

    @classmethod
    async def get_crew_groups_list(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._inline_request('common_api', '1.0', data,
                                         request=request, method='GET')

    @classmethod
    async def get_crews_info(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._inline_request('common_api', '1.0', data,
                                         request=request, method='GET')

    @classmethod
    async def get_tariffs_list(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._inline_request('common_api', '1.0', data,
                                         request=request, method='GET')

    @classmethod
    async def get_services_list(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._inline_request('common_api', '1.0', data,
                                         request=request, method='GET')

    @classmethod
    async def get_discounts_list(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._inline_request('common_api', '1.0', data,
                                         request=request, method='GET')

    @classmethod
    async def get_current_orders(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._inline_request('common_api', '1.0', data,
                                         request=request, method='GET')

    @classmethod
    async def get_info_by_order_id(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._inline_request('tm_tapi', '1.0', data,
                                         request=request, method='GET')

    @classmethod
    async def change_order_state(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._inline_request('tm_tapi', '1.0', data,
                                         request=request, method='POST')

    @classmethod
    async def create_order2(cls, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await cls._json_request('common_api', '1.0', data,
                                       request=request, method='POST')

    @classmethod
    async def get_order_state_id(cls, state_name, *args, **kwargs):
        with await aiopg.connect(DSN) as pgcon:
            with await pgcon.cursor() as c:
                await c.execute('select settings, id from order_states where is not null;')
                async for r in c:
                    sets = xmltodict.parse(r[0])
                    if int(get_value('settings.oktell.to_client.use_call_back', sets)):
                        event_name = get_value(
                            'settings.oktell.to_client.script_name', sets).upper()
                    if event_name == state_name:
                        return r[1]
