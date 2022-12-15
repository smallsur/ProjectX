from datetime import datetime
import pytz
from neomodel import StructuredRel, DateProperty, StringProperty, IntegerProperty


class Material_Reserved(StructuredRel):
    on_date = DateProperty(default=lambda: datetime.now(pytz.utc))
    num_unssign = IntegerProperty(label='num_unssign')
    num_assign = IntegerProperty(label='num_assign')

    num_store = IntegerProperty(label='num_store')


class Truck_Include(StructuredRel):
    on_date = DateProperty(default=lambda: datetime.now(pytz.utc))
    num_truck = IntegerProperty(label='num_truck')