Md5_server
=====

Preparations
------------

Run Postgres DB server:

    $ docker run --rm -it -p 5432:5432 postgres:10

Create db:

    $ python init_db.py


Run
---
Run application:

    $ python aiohttpdemo_md5/main.py
