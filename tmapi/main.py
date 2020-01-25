from core import TMAPI
import asyncio
from aiohttp import web
from core.parsers import request_parser


routes = web.RouteTableDef()


@routes.get('/execsvcscript')
async def oktell_request(request):
    _request = request_parser(request.rel_url.query)

    return web.Response()


def main():
    app = web.Application()
    app.router.add_routes(routes)
    web.run_app(app)
