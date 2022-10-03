import os

from aiohttp import web

from app import BASE_DIR
from app.base.application import View
from app.store.ws.ws_accessor import WSContext


class IndexView(View):
    async def get(self):
        with open(os.path.join(BASE_DIR, 'client', 'index.html'), 'r') as f:
            file = f.read()

        return web.Response(
            body=file,
            headers={
                'Content-Type': 'text/html',
            }
        )


class WSConnectView(View):
    async def get(self):
        async with WSContext(
                accessor=self.store.ws_accessor,
                request=self.request,
                close_callback=self.store.geo_manager.on_user_disconnect,
        ) as connection_id:
            await self.store.geo_manager.handle(connection_id)
        return
