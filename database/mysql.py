import pymysql
import aiomysql
import asyncio

from utils import Singleton
from utils import checkFunctions
from utils import Log

TEXT_DB = {"host": "114.213.213.163", "port": 3306, "user": "awen", "password": "123456",
           "database": "DispatchDatabase", 'charset': 'utf8', 'autocommit': True,
            'maxsize': 10, 'minsize': 1, 'echo': False, 'pool_recycle': -1}

__loop = asyncio.get_event_loop()

#检查参数
@checkFunctions.register
def checkMysqlDb(cfg):
    assert getattr(cfg, 'mysql') is not None

    config_mysql = getattr(cfg, 'mysql')

    for k,v in config_mysql:
        assert k in TEXT_DB.keys()


class MysqlDbPool(Singleton):
    __pool = None

    def __init__(self, cfg=None):
        assert cfg is not None


        config_mysql = getattr(cfg, 'mysql')

        for k, v in TEXT_DB.items():
            if getattr(config_mysql, k) is not None:
                TEXT_DB[k] = getattr(config_mysql, k)

        self.__init_pool()

    #异步初始化连接池
    async def __init_pool(self):
        if MysqlDbPool.__pool is None:
            MysqlDbPool.__pool = await aiomysql.create_pool(**TEXT_DB, loop=__loop)
    

    @classmethod
    async def select(cls, sql, size = 0):
        async with cls.__pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql)
                    if size:
                        rs = await cur.fetchmany(size)
                    else:
                        rs = await cur.fetchall()

        cls.__pool.close()
        await cls.__pool.wait_closed()
        return rs

    


    



