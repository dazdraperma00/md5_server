from sqlalchemy import create_engine, MetaData

from aiohttpdemo_md5.settings import config
from aiohttpdemo_md5.db import md5_storage


DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

admin_db_url = DSN.format(
    user='postgres', password='postgres', database='postgres',
    host='localhost', port=5432
)

user_db_url = DSN.format(**config['postgres'])

admin_engine = create_engine(admin_db_url, isolation_level='AUTOCOMMIT')
user_engine = create_engine(user_db_url)


def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[md5_storage])


def setup_db(config):

    db_name = config['database']
    db_user = config['user']
    db_pass = config['password']

    conn = admin_engine.connect()
    conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
    conn.execute("DROP ROLE IF EXISTS %s" % db_user)
    conn.execute("CREATE USER %s WITH PASSWORD '%s'" % (db_user, db_pass))
    conn.execute("CREATE DATABASE %s ENCODING 'UTF8'" % db_name)
    conn.execute("GRANT ALL PRIVILEGES ON DATABASE %s TO %s" %
                 (db_name, db_user))
    conn.close()


def teardown_db(config):

    db_name = config['database']
    db_user = config['user']

    conn = admin_engine.connect()
    conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
    conn.execute("DROP ROLE IF EXISTS %s" % db_user)
    conn.close()


if __name__ == '__main__':
    setup_db(config['postgres'])
    create_tables(user_engine)

    # teardown_db(config['postgres'])
