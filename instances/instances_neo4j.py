from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      UniqueIdProperty, RelationshipTo, BooleanProperty, RelationshipFrom, 
                      One, OneOrMore, ZeroOrMore, ZeroOrOne)

from .relationship_neo4j import Material_Reserved, Truck_Include


# 物资表,一般属性存放在mysql
class Material_Node(StructuredNode):

    id = UniqueIdProperty()
    material_id = IntegerProperty(unique_index=True, required=True, label='material_id')

    name = StringProperty(label='material_name')
    
    include_parent_material = RelationshipFrom('Material_Standard_Node', 'INCLUDE_MATERIAL', cardinality=ZeroOrOne)


class Material_Standard_Node(StructuredNode):
    id = UniqueIdProperty()
    material_standard_id = IntegerProperty(unique_index=True, required=True, label='material_standard_id')
    name = StringProperty(label='material_stanard_name')

    include_material = RelationshipTo('Material_Node', 'INCLUDE_MATERIAL', cardinality=ZeroOrMore)

    include_parent_material = RelationshipFrom('Material_Standard_Node', 'INCLUDE_STANDRAD_MATERIAL', cardinality=ZeroOrOne)
    include_standard_material = RelationshipTo('Material_Standard_Node', 'INCLUDE_STANDRAD_MATERIAL', cardinality=ZeroOrMore)


class District_Node(StructuredNode):
    id = UniqueIdProperty()

    district_id = IntegerProperty(unique_index=True, required=True, label='district_id')

    name = StringProperty(label='location_name')

    level = StringProperty(label='level')

    center = StringProperty(lebel='center')

    parent_id = IntegerProperty(required=True, label='parent_id')

    include = RelationshipTo("District_Node", "INCLUDE_DISTRICT")

    include_reserve_point = RelationshipTo("Reserve_Point_Node", "INCLUDE_RESERVE_POINT")


class Reserve_Point_Node(StructuredNode):
    id = UniqueIdProperty()

    node_id = IntegerProperty(unique_index=True, label='node_id')
    name = StringProperty(label='reserve_point_name')
    is_allocated = BooleanProperty(label='is_allocated')

    include_material = RelationshipTo("Material_Node", "RESERVED_MATERIAL", model=Material_Reserved)

    include_truck = RelationshipTo("Truck_Node", "INCLUDE_TRUCK", model=Truck_Include, cardinality=ZeroOrMore)

class Truck_Node(StructuredNode):
    id = UniqueIdProperty()

    licence = StringProperty(label='licence')

    point = RelationshipFrom('Reserve_Point_Node', "INCLUDE_TRUCK", model=Truck_Include, cardinality=ZeroOrOne)



