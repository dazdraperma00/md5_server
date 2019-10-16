from aiohttp import web

from routes import setup_routes

from settings import config
from db import close_pg, init_pg


app = web.Application()
setup_routes(app)
app['config'] = config

app.on_startup.append(init_pg)
app.on_cleanup.append(close_pg)
# setup(app)
web.run_app(app)
