import logging
import aioredis
from aiohttp import web
import aiohttp_jinja2
import jinja2
from marshmallow import fields, Schema
from aiohttp_apispec import docs, querystring_schema, validation_middleware, setup_aiohttp_apispec


import settings
from core.parsers import request_parser
from .config import PORT, TEMPLATES
from .handlers import select_handlers

LOGGER = logging.getLogger()
routes = web.RouteTableDef()

DEBUG = True

if DEBUG:
    import aiohttp_autoreload
    aiohttp_autoreload.start()


class OktellRequestSchema(Schema):
    order_id = fields.Integer(data_key='startparam4')
    phone = fields.String(name='startparam1')
    callback_state = fields.Integer(attribute='startparam3')
    event = fields.String(attribute='name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


async def create_engines(app):
    app['redis'] = await aioredis.create_redis_pool(settings.REDIS_HOST)


async def dispose_engines(app):
    app['redis'].close()
    await app['redis'].wait_closed()


@routes.get('/execsvcscript')
# @request_schema(OktellRequestSchema, locations=['query'])
@querystring_schema(OktellRequestSchema(), locations=['query'], put_into='data')
async def oktell_request(request, **data):
    _request = await request_parser(request.rel_url.query)
    handlers = select_handlers(_request.get('event'))
    for handler in handlers:
        await handler(_request, request.app, LOGGER)
    return web.Response()


def main():
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(TEMPLATES))
    app.router.add_routes(routes)
    # app.middlewares.append(validation_middleware)
    # setup_aiohttp_apispec(app=app,
    #                     request_data_name='validated_data',
    #                     title='My Documentation',
    #                     version='v1',
    #                     url='/execsvcscript')
    app.on_startup.append(create_engines)
    app.on_cleanup.append(dispose_engines)
    web.run_app(app, port=PORT)
