class Field(object):

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default
        self.comment = None

    def __str__(self):
        return '<%s, %s@%s: %s>' % (self.__class__.__name__, self.column_type, self.name, self.comment)


class StringField(Field):
    def __init__(self, name=None, primary_key=False, default=None):
        super().__init__(name, 'varchar', primary_key, default)


class BooleanField(Field):
    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)


class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'int', primary_key, default)


class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'float', primary_key, default)


class TextField(Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)


class DatetimeField(Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, 'Datetime', False, default)
