import uuid

import aiopg.sa
from sqlalchemy import (
    MetaData, Table, Column, String
)
from sqlalchemy.dialects import postgresql


def generate_uuid():
    return str(uuid.uuid4())


meta = MetaData()

md5_storage = Table(
    'md5_storage', meta,

    Column("uuid", postgresql.UUID, primary_key=True, default=generate_uuid),
    Column('status', String(200), nullable=False),
    Column('email', String),
    Column('md5', String),
    Column('url', String, nullable=False),
)


async def init_pg(app):
    conf = app['config']['postgres']
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
    )
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()
