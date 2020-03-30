import aiohttp_jinja2
from aiohttp import web


routes = web.RouteTableDef()

@routes.view('/login')
class Login(web.View):
    async def post(self):
        context = {}
        response = aiohttp_jinja2.render_template('login.html', self.request, context)
        response.headers['Content-Language'] = 'ru'
        return response

    async def get(self, request):
        context = {}
        response = aiohttp_jinja2.render_template('login.html', self.request, context)


@routes.view('/')
class Index(web.View):
    async def post(self):
        pass

    async def get(self):
        pass

    async ws(self):
        pass

