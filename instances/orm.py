from database import execute_sql_task

from .field import Field


class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        # 排除Model类本身:
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        # 获取table名称:
        tableName = attrs.get('__table__', None) or name
        # 获取所有的Field和主键名:
        mappings = dict()
        fields = []
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                mappings[k] = v
                if v.primary_key:
                    # 找到主键:
                    if primaryKey:
                        raise RuntimeError('Duplicate primary key for field: %s' % k)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise RuntimeError('Primary key not found.')
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f: '`%s`' % mappings[f].name, fields))
        attrs['__mappings__'] = mappings  # 保存属性和列的映射关系
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey  # 主键属性名
        attrs['__fields__'] = fields  # 除主键外的属性名
        # 构造默认的SELECT, INSERT, UPDATE和DELETE语句:
        attrs['__select__'] = 'select `%s`, %s from `%s` ' % (primaryKey, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) ' % (tableName, ', '.join(escaped_fields), primaryKey)
        attrs['__update__'] = 'update `%s` ' % tableName
        attrs['__delete__'] = 'delete from `%s`' % tableName
        return type.__new__(cls, name, bases, attrs)

    def __init__(cls, names, bases, attrs):
        super().__init__(names, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                setattr(self, key, value)
        return value

    @staticmethod
    def __get_kv_string(keys, values, separator=','):
        s = []
        if keys is None or not isinstance(keys, list):
            s.extend(values)
        else:
            for k, v in zip(keys, values):
                s.append(' `%s` = %s ' % (k, v))
        return separator.join(s)

    @classmethod
    async def findByKeys(cls, keys: list = [], values: list = [], **kwargs):
        keys = list(map(lambda x: cls.__mappings__[x].name, keys))
        sql = '%s where ' % cls.__select__ + cls.__get_kv_string(keys=keys, values=values, separator='and')

        rs = await execute_sql_task(sql, type_sql='select', size=0)

        return rs

    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        sql = self.__insert__ + 'values(%s)' % (self.__get_kv_string(keys=None, values=args, separator=','))

        rows = await execute_sql_task(sql=sql, type_sql='insert')

        if rows == 0:
            raise RuntimeError('excute failed!')

        return rows

    async def update(self):
        args = list(map(self.getValue, self.__fields__))

        sql = self.__update__ + 'set %s ' % (self.__get_kv_string(keys=self.__fields__, values=args))
        sql = sql + 'where %s' % (
            self.__get_kv_string(keys=[self.__primary_key__, ], values=[self.getValue(self.__primary_key__), ]))

        rows = await execute_sql_task(sql=sql, type_sql='update')

        if rows == 0:
            raise RuntimeError('excute failed!')

        return rows

    async def delete(self):
        sql = self.__delete__ + 'where %s ' % (
            self.__get_kv_string(keys=[self.__primary_key__, ], values=[self.getValue(self.__primary_key__), ]))

        rows = await execute_sql_task(sql=sql, type_sql='delete')

        if rows == 0:
            raise RuntimeError('excute failed!')

        return rows
