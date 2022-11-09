from typing import List
from neomodel import db

from .sqlalchemy import get_session
from .graphdb import url
from instances import District, District_Node


def get_all_district()->List[District]:
    rs = None
    with get_session() as s:
        rs  =  s.query(District)

    return rs

@db.transaction
def create_or_update_district():
    rs = get_all_district()
    district_nodes =[]
    for d in rs:
        district_nodes.append({'district_id':d.id, 'name':d.name, 'suffix':d.suffix, 'parent_id':d.parent_id})

    District_Node.create_or_update(district_nodes)
    for node in District_Node.nodes:
        District_Node.nodes.filter(id = )

    # for k, v in district_nodes_dict.items():
    #     if district_nodes_dict.get(v.parent_id, None) is None:
    #         continue
    #     if district_nodes_dict[v.parent_id].include.relationship(v) is None:
    #         rel = district_nodes_dict[v.parent_id].include.connect(v)
    #         rel.save()
