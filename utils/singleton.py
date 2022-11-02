class SingletonType(type):
    def __new__(mcs, names, bases, attrs):
        return super(SingletonType, mcs).__new__(mcs, names, bases, attrs)

    def __init__(cls, names, bases, attrs):
        cls._instance = None
        super().__init__(names, bases, attrs)

    def __call__(cls, names, bases, attrs):
        if cls._instance is None:
            cls._instance = cls.__new__()
            cls._instance.__init__(names, bases, attrs)

        return cls._instance


class Singleton(object, metaclass=SingletonType):

    pass
