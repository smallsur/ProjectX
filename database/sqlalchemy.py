import contextlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config


TEXT_DB = {'url': 'mysql+pymysql://awen:123456@121.5.62.4/DispatchDatabase?charset=utf8mb4',
            'echo': True,
            'pool_size': 10,
            'max_overflow': 10, 'connect_args':{'connect_timeout': 10}}


for k, v in TEXT_DB.items():
    c = getattr(config.cfg, 'sqlalchemy',None)
    if c is not None:
        TEXT_DB[k] = getattr(c, k)

engine = create_engine(**TEXT_DB)


@contextlib.contextmanager
def get_session():
    Session = sessionmaker(bind=engine)
    s = Session()
    try:
        yield s
        s.commit()
    except Exception as e:
        s.rollback()
        raise e
    finally:
        s.close()