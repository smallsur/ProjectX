import sys
from typing import List
from neomodel import db
import logging

import config
from utils import get_log_format

from .sqlalchemy import get_session
from .graphdb import url
from instances import District, District_Node, Reserve_Point

_logger = logging.getLogger(__name__)
_logger.setLevel(getattr(logging, getattr(config.cfg, 'loglevel')))
_handler = logging.StreamHandler(stream=sys.stdout)
_handler.setFormatter(logging.Formatter(get_log_format(thread_info=True)))
_logger.addHandler(_handler)


def get_all_district() -> List[District]:
    rs = None
    with get_session() as s:
        rs = s.query(District)

    return rs


def get_all_reserve_point() -> List[Reserve_Point]:
    rs = None
    with get_session() as s:
        rs = s.query(Reserve_Point)

    return rs


@db.transaction
def create_or_update_district():
    rs = get_all_district()

    _logger.info('create or update district_node, running....')
    district_nodes = []
    for d in rs:
        district_nodes.append({'district_id': d.id, 'name': d.name, 'suffix': d.suffix, 'parent_id': d.parent_id})

    created_nodes = District_Node.create_or_update(*district_nodes, kwargs={})
    _logger.info('create or update district_node completed! node_nums is %d' % len(created_nodes))

    return created_nodes


@db.transaction
def create_or_update_district_include_rel():
    _logger.info('create or update district <include> relationship, running....')
    count = 0
    for node in District_Node.nodes:
        parent_id = node.parent_id

        if parent_id == 0:
            continue
        parent_node = District_Node.nodes.get(district_id=parent_id)

        if parent_node.include.relationship(node) is None:
            rel = parent_node.include.connect(node)
            # rel.save()
            _logger.debug('save district relationship from %s to %s' % (parent_node, node))
            count += 1

    _logger.info('create or update district <include> relationship completed! rel_nums is %d' % count)


def crete_or_update_reserve_point():
    _logger.info('create or update reserve point , running....')

    rs = get_all_reserve_point()

    reserve_points = []
    for row in rs:
        reserve_points.append({'node_id': row.id, 'name': row.name, })


