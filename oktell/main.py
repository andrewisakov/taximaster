import logging
import aioredis
from aiohttp import web

import settings
from core.parsers import request_parser
from .handlers import select_handlers

LOGGER = logging.getLogger()
routes = web.RouteTableDef()

DEBUG = True

if DEBUG:
    import aiohttp_autoreload
    aiohttp_autoreload.start()


async def create_engines(app):
    # await routes.setup(app)
    app['redis'] = await aioredis.create_redis_pool(settings.REDIS_HOST)


async def dispose_engines(app):
    # app['redis'].stop()
    app['redis'].close()
    await app['redis'].wait_closed()


@routes.get('/execsvcscript')
async def oktell_request(request):
    _request = request_parser(request.rel_url.query)
    handlers = select_handlers(_request.get('event'))
    for handler in handlers:
        await handler(_request, request.app, LOGGER)
    return web.Response()


def main():
    app = web.Application()
    app.router.add_routes(routes)
    app.on_startup.append(create_engines)
    app.on_cleanup.append(dispose_engines)
    web.run_app(app)
