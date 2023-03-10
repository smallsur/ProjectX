from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String, DateTime, FLOAT, SMALLINT, ForeignKey, BOOLEAN, Text
from sqlalchemy.orm import relationship

ModelBase = declarative_base()


class Material_Standard(ModelBase):
    __tablename__ = 'table_material_standard'

    minor_code = Column('minor_category_code', Integer, primary_key=True)
    minor_name = Column('minor_category_name', String(length=20))

    note = Column('notes', String(length=255))

    medium_code = Column('medium_category_code', Integer)
    medium_name = Column('medium_category_name', String(length=20))

    major_code = Column('major_category_code', Integer)
    major_name = Column('major_category_name', String(length=20))

    fine_material = relationship('Material', back_populates='classification')

    fine_truck = relationship('Truck', back_populates='material_standard')


class Material(ModelBase):
    __tablename__ = 'table_material'

    id = Column('id', Integer, primary_key=True)

    name = Column('name', String(length=20))

    weight = Column('weight', FLOAT)

    height = Column('height', FLOAT)

    width = Column('width', FLOAT)

    length = Column('length', FLOAT)

    code = Column('code', Integer, ForeignKey("table_material_standard.minor_category_code"))

    classification = relationship("Material_Standard", back_populates='fine_material')



class Truck(ModelBase):
    __tablename__ = 'table_truck'

    licence = Column('licence', String(length=10), primary_key=True)

    wheelbase = Column('wheelbase', Integer)

    type = Column('type', String(length=10))

    weight = Column('weight', FLOAT)
    capacity = Column('capacity', FLOAT)

    front_axle_load = Column('front_axle_load', FLOAT)
    after_axle_load = Column('after_axle_load', FLOAT)

    length = Column('length', FLOAT)
    width = Column('width', FLOAT)
    height = Column('height', FLOAT)

    box_length = Column('box_length', FLOAT)
    box_width = Column('box_width', FLOAT)

    drive = Column('drive', Integer)
    power = Column('power', FLOAT)

    # 'railings', 'flat', 'box', 'grid', 'pot', 'auto'
    carriage_structure = Column('carriage_structure', String(10))

    speed_max = Column('speed_max', FLOAT)
    speed_average = Column('speed_average', FLOAT)

    # 'another', 'country_III', 'country_IV', 'country_V'
    emission = Column('emission', String(length=10))
    # 'diesel', 'gasoline', 'another'
    energy = Column('energy', String(length=10))
    fuel_capacity = Column('fuel_capacity', Integer)

    location = Column('location', String(length=255))
    register_location = Column('register_location', String(length=255))
    date_manufacture = Column('date_manufacture', DateTime)
    code = Column('code', Integer, ForeignKey("table_material_standard.minor_category_code"))

    driver = relationship('Truck_Driver', back_populates='truck')
    material_standard = relationship('Material_Standard', back_populates='fine_truck')


class Truck_Driver(ModelBase):
    __tablename__ = 'table_truck_driver'

    name = Column('name', String(length=10))

    idcard = Column('idcard', String(length=25), primary_key=True)

    phonenumber = Column('phonenumber', String(length=15))

    licence = Column('licence', String(length=10), ForeignKey("table_truck.licence"), nullable=False)

    truck = relationship('Truck', back_populates='driver')


class Reserve_Point(ModelBase):
    __tablename__ = 'table_reserve_point'

    id = Column('id', Integer, primary_key=True)

    name = Column('name', String(length=20))

    longitude = Column('longitude', FLOAT, nullable=True)
    latitude = Column('latitude', FLOAT, nullable=True)

    district_id = Column('district_id', SMALLINT, ForeignKey("table_district_standard.id"), nullable=False)

    allocated = Column('allocated', BOOLEAN)

    district = relationship("District_Standard", back_populates='reserve_point')



class District_Standard(ModelBase):
    __tablename__ = 'table_district_standard'

    id = Column('id', SMALLINT, primary_key=True)
    name = Column('name', String(length=270))
    parent_id = Column('parent_id', SMALLINT, ForeignKey('table_district_standard.id'))

    adcode = Column('adcode', Integer)
    citycode = Column('citycode', Integer)
    center = Column('center', String(length=50))
    level = Column('level', String(length=20))
    polyline = Column('polyline', Text)
    reserve_point = relationship("Reserve_Point", back_populates='district')
    child  = relationship("District_Standard")#subquery,select,lazy='joined'