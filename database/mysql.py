import pymysql
import aiomysql
import asyncio

from config import cfg
from utils import Log

TEXT_DB = {"host": "114.213.213.163", "port": 3306, "user": "awen", "password": "123456",
           "db": "DispatchDatabase", 'charset': 'utf8', 'autocommit': True,
           'maxsize': 10, 'minsize': 1, 'echo': False, 'pool_recycle': -1}

__loop = asyncio.get_event_loop()

__pool = None


async def get_pool():
    global __pool, __loop

    config_mysql = getattr(cfg, 'mysql')

    for k, v in TEXT_DB.items():
        if getattr(config_mysql, k, None) is not None:
            TEXT_DB[k] = getattr(config_mysql, k)

    Log.logInfo(level=0, message='initting the pool of mysql')

    __pool = await aiomysql.create_pool(**TEXT_DB, loop=__loop)


__loop.run_until_complete(get_pool())


async def select(sql, size=0, **kwargs):
    global __pool
    async with __pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql)
            if size > 0:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()

    __pool.close()
    await __pool.wait_closed()
    return rs


async def execute(sql):
    global __pool
    async with __pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql)
            affected = cur.rowcount

    __pool.close()
    await __pool.wait_closed()
    return affected


async def execute_sql_task(sql, type_sql='select', size=0):
    global __loop
    if type_sql == 'select':
        rs = await select(sql, size=size)

    else:
        rs = await execute(sql)

    return rs
