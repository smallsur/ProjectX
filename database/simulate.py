import sys
import logging
from typing import List
from neomodel import db
from sqlalchemy import (insert, select, update, delete)

import config
from utils import get_log_format

from .sqlalchemy import get_session
from .graphdb import url
from instances import (District, District_Node, Reserve_Point, Reserve_Point_Node,
                       Material_Standard, Material, Material_Node)


_logger = logging.getLogger(__name__)
_logger.setLevel(getattr(logging, getattr(config.cfg, 'loglevel')))
_handler = logging.StreamHandler(stream=sys.stdout)
_handler.setFormatter(logging.Formatter(get_log_format(thread_info=True)))
_logger.addHandler(_handler)

def getdistrict_by_name(name:str):
    with get_session as s:
        sql = District.
        s.excute()


@db.transaction
def simulate_one_district():
    pass

@db.transaction
def simulate_one_reserve_point():
    pass
