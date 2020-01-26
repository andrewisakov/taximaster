import datetime
import hashlib
import inspect
import json
import urllib.parse

import aiohttp

import xmltodict

from settings import SAULT, SERVICE_ROOT_DIR, TM_HOST, TM_PORT


class TMAPIBase:
    CONTENT_TYPE_X_WWW_FORM_URLENCODED = 'application/x-www-form-urlencoded'
    CONTENT_TYPE_APP_JSON = 'application/json'
    INLINE_SIGN = ['set_request_state',
                   'get_info_by_order_id',
                   'change_order_state']

    async def _request(self, method, url, headers, data=None, json=None):
        method = method.lower()
        response = None
        context = ssl._create_unverified_context()

        async with aiohttp.ClientSession(headers=headers) as session:
            method = getattr(session, f'_{method.lower()}')
            async with method(url, data=data, json=json, ssl=context) as r:
                response = r
        return response

    def _signature(self, data):
        return hashlib.md5((data+SAULT).encode()).hexdigest()

    async def _inline_request(self, api, ver, data, request, method='GET'):
        method = method.upper()
        url = f'https://{TM_HOST}:{TM_PORT}/{api}/{ver}/{request}'
        params = urllib.parse.urlencode(data)
        _signature = self._signature(params)

        headers = {'Signature': _signature,
                   'Content-Type': self.CONTENT_TYPE_X_WWW_FORM_URLENCODED,
                   }

        if request in self.INLINE_SIGN:
            params += f'&signature={_signature}'

        if method == 'GET':
            url += f'?{params}'
            params = None

        response = await self._request(method, url, headers, data=params)

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

    async def _json_request(self, api, ver, data, request, method='POST'):
        url = f'https://{TM_HOST}:{TM_PORT}/{api}/{ver}/{request}'
        headers = {'Signature': self._signature(data),
                   'Content-Type': self.CONTENT_TYPE_APP_JSON,
                   }
        await self._request(method.lower(), url, headers, json=data)
        return


class TMAPI(TMAPIBase):
    async def get_request_state(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._inline_request('tm_tapi', '1.0', data,
                                          request=request, method='POST')

    async def create_driver_operation(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._json_request('common_api', '1.0', data,
                                        request=request, method='POST')

    async def save_client_feed_back(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._json_request('common_api', '1.0', data,
                                        request=request, method='POST')

    async def ping(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._inline_request('common_api', '1.0', data,
                                          request=request, method='GET')

    async def get_finished_orders(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._inline_request('common_api', '1.0', data,
                                          request=request, method='GET')

    async def get_drivers_info(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._inline_request('common_api', '1.0', data,
                                          request=request, method='GET')

    async def get_driver_info(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._inline_request('common_api', '1.0', data,
                                          request=request, method='GET')

    async def get_order_state(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._inline_request('common_api', '1.0', data,
                                          request=request, method='GET')

    async def check_authorization(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._inline_request('common_api', '1.0', data,
                                          request=request, method='GET')

    async def get_car_info(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._inline_request('common_api', '1.0', data,
                                          request=request, method='GET')

    async def get_crew_groups_list(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._inline_request('common_api', '1.0', data,
                                          request=request, method='GET')

    async def get_crews_info(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._inline_request('common_api', '1.0', data,
                                          request=request, method='GET')

    async def get_tariffs_list(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._inline_request('common_api', '1.0', data,
                                          request=request, method='GET')

    async def get_services_list(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._inline_request('common_api', '1.0', data,
                                          request=request, method='GET')

    async def get_discounts_list(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._inline_request('common_api', '1.0', data,
                                          request=request, method='GET')

    async def get_current_orders(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._inline_request('common_api', '1.0', data,
                                          request=request, method='GET')

    async def get_info_by_order_id(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._inline_request('tm_tapi', '1.0', data,
                                          request=request, method='GET')

    async def change_order_state(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._inline_request('tm_tapi', '1.0', data,
                                          request=request, method='POST')

    async def create_order2(self, data, *args, **kwargs):
        request = inspect.currentframe().cu_frame.f_code.co_name
        return await self._json_request('common_api', '1.0', data,
                                        request=request, method='POST')
