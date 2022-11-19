import sys
from typing import List
from neomodel import db
import logging

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


def get_all_district() -> List[District]:
    with get_session() as s:
        rs = s.query(District)
    return rs


def get_all_reserve_point() -> List[Reserve_Point]:
    with get_session() as s:
        rs = s.query(Reserve_Point)
    return rs

def get_all_material_standard() ->List[Material_Standard]:
    with get_session() as s:
        rs = s.query(Material_Standard)
    return rs

@db.transaction
def clear_graphdb():
    db.cypher_query(query='match (n) detach delete n', params=None)


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


@db.transaction
def crete_or_update_reserve_point():
    _logger.info('create or update reserve point , running....')

    rs = get_all_reserve_point()

    count_node, count_rel = 0, 0
    for row in rs:
        new_reserve_point = Reserve_Point.nodes.get_or_none(node_id=row.id)

        # 生成储备点
        if new_reserve_point is None:
            new_reserve_point = Reserve_Point_Node(node_id=row.id, name=row.name, is_allocated=row.allocated)
            _logger.debug('save reserve point %s ' % new_reserve_point.name)
            # 生成地区的储备点关系
        else:
            new_reserve_point.name = row.name
            new_reserve_point.is_allocated = row.allocated
            _logger.debug('update reserve point %s ' % new_reserve_point.name)

        new_reserve_point.save()

        district = District_Node.nodes.get_or_none(district_id=row.district_id)
        if district is not None and district.include_reserve_point.relationship(new_reserve_point) is None:
            district.include_reserve_point.connect(new_reserve_point)
            logging.debug('add reserve point to district %s' % district.name)

        _logger.info('create or update reserve point node nums: %d, relationship nums: %d ' % (count_node, count_rel))

@db.transaction
def create_or_update_material():
    pass