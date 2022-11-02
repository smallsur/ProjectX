from .field import *
from .orm import Model


class Material(Model):
    __table__ = 'table_material'

    id = IntegerField('id', True)
    name = StringField('name', False)

    level = IntegerField('level_realtime', False)

    weight_lower = FloatField('weight_limit_lower', False)
    weight_upper = FloatField('weight_limit_upper', False)

    height_upper = FloatField('height_limit_upper', False)
    height_lower = FloatField('height_limit_lower', False)

    width_upper = FloatField('width_limit_upper', False)
    width_lower = FloatField('width_limit_lower', False)

    length_upper = FloatField('length_limit_upper', False)
    length_lower = FloatField('length_limit_lower', False)


class Truck(Model):
    __table__ = 'table_truck'


class Driver(Model):
    __table__ = 'table_truck_driver'
