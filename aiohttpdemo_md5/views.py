import asyncio
import hashlib
import uuid

import aiopg
import sqlalchemy as sa
import aiohttp
from aiohttp import web

import db


async def submit(request):
    data = await request.read()

    if not data:
        return web.HTTPBadRequest()

    params = data.decode('utf-8').split('&')

    print(params)

    if len(params) > 2:
        return web.HTTPBadRequest()

    new_data = dict()
    for item in params:
        a, b = item.split('=')
        new_data[a] = b

    file_url = new_data.get('url', None)
    email = new_data.get('email', None)
    id = str(uuid.uuid4())
    status = 'running'

    #  Запись в БД
    async with request.app['db'].acquire() as conn:
        await conn.execute(db.md5_storage.insert().values(uuid=id,
                                                          status=status,
                                                          email=email,
                                                          url=file_url
                                                          ))

    chunk_size = 20

    asyncio.ensure_future(get_md5(request.app, id, file_url, chunk_size))

    data = {}
    data['id'] = str(id)

    return web.json_response(data, status=200)


async def check(request):
    id = request.query['id']
    data = {}

    async with request.app['db'].acquire() as conn:

        try:
            async for row in conn.execute(db.md5_storage.select().where(db.md5_storage.c.uuid == id)):
                status = row.status
                if status == 'done':
                    data['md5'] = row.md5
                    data['url'] = row.url
                data['status'] = status
            if not data:
                data['status'] = "doesn't exist"
        except aiopg.connection.psycopg2.Error:
            return web.HTTPBadRequest()

    return web.json_response(data, status=200)


async def get_md5(app, id, url, chunk_size):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            print(resp.status)
            md5 = hashlib.md5()

            while True:
                chunk = await resp.content.read(chunk_size)
                if not chunk:
                    break
                md5.update(chunk)

    md5 = md5.hexdigest()

    email = None
    # Запись в БД
    async with app['db'].acquire() as conn:
        await conn.execute(sa.update(db.md5_storage).values({'md5': md5, 'status': 'done'})
                           .where(db.md5_storage.c.uuid == id))

        async for row in conn.execute(db.md5_storage.select().where(db.md5_storage.c.uuid == id)):
            email = row.email

    # Отправка md5 на почту
    # if email:
    #     message = MIMEText(f"url: {url}/md5: {md5}")
    #     message["From"] = "root@localhost"
    #     message["To"] = email
    #     message["Subject"] = "Hello World!"
    #
    #     await aiosmtplib.send(message, hostname="127.0.0.1", port=1025)
