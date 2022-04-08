import os

from aiohttp import web

from app import BASE_DIR
from app.base.application import View


class IndexView(View):
    async def get(self):
        with open(os.path.join(BASE_DIR, 'client', 'index.html'), 'r') as f:
            file = f.read()

        return web.Response(body=file, headers={
            'Content-Type': 'text/html',
        })


class ConnectView(View):
    async def get(self):
        ws = await self.store.ws.handle_request(self.request)
        return ws
