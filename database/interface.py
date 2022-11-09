from typing import List


from .sqlalchemy import get_session
from .graphdb import url
from instances import District, District_Node


def get_all_district()->List[District]:
    rs = None
    with get_session() as s:
        rs  =  s.query(District)

    return rs


def create_or_update_district():
    rs = get_all_district()
    district_nodes = {}
    for d in rs:
        district_nodes[d.id] = District_Node(district_id=d.id, name=d.name,
                                    suffix=d.suffix, parent_id=d.parent_id)
    
    District_Node.create_or_update(district_nodes.values())

    for k, v in district_nodes.items():
        if district_nodes.get(v.parent_id, None) is None:
            continue
        if district_nodes[v.parent_id].include.relationship(v) is None:
            rel = district_nodes[v.parent_id].include.connect(v)
            rel.save()

