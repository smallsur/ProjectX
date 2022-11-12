from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      UniqueIdProperty, RelationshipTo, RelationshipFrom)

from .relationship_neo4j import Material_Include, Truck_Include


# 物资表,一般属性存放在mysql
class Material_Node(StructuredNode):
    id = UniqueIdProperty()
    material_id = IntegerProperty(unique_index=True, required=True, label='material_id')

    name = StringProperty(label='material_name')
    num_unassign = IntegerProperty(label='num_unassign')
    num_assign = IntegerProperty(label='num_assign')

    num_store = IntegerProperty(label='num_store')


class Truck_Node(StructuredNode):
    id = UniqueIdProperty()

    license = StringProperty(unique_index=True, required=True, label='licence')


class District_Node(StructuredNode):
    id = UniqueIdProperty()

    district_id = IntegerProperty(unique_index=True, required=True, label='district_id')

    name = StringProperty(label='location_name')

    suffix = StringProperty(label='suffix')

    parent_id = IntegerProperty(required=True, label='parent_id')

    include = RelationshipTo("District_Node", "INCLUDE_DISTRICT")

    include_reserve_point = RelationshipTo("Reserve_Point_Node", "INCLUDE_RESERVE_POINT")


class Reserve_Point_Node(StructuredNode):
    id = UniqueIdProperty()

    node_id = IntegerProperty(unique_index=True, label='node_id')
    name = StringProperty(label='reserve_point_name')

    include = RelationshipTo("Material_Node", "INCLUDE_MATERIAL", model=Material_Include)

    include_truck = RelationshipTo("Truck_Node", "INCLUDE_TRUCK", model=Truck_Include)
