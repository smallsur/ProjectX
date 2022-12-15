import sys
import logging
from typing import List
from neomodel import db
from sqlalchemy import (insert, select, update, delete)

import config
from utils import get_log_format

from .sqlalchemy import get_session
from .graphdb import url
from instances import (Truck_Driver, Truck, District_Node, District_Standard, Material, 
                        Material_Node, Material_Reserved, Material_Standard, Material_Standard_Node, 
                        Reserve_Point, Reserve_Point_Node)


_logger = logging.getLogger(__name__)
_logger.setLevel(getattr(logging, getattr(config.cfg, 'loglevel')))
_handler = logging.StreamHandler(stream=sys.stdout)
_handler.setFormatter(logging.Formatter(get_log_format(thread_info=True)))
_logger.addHandler(_handler)


