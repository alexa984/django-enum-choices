from enum import Enum, auto


# Standard enum
class MyEnum(Enum):
    A = 'a'
    B = 'b'


# Enum with custom readable values
class CustomReadableValueEnum(Enum):
    A = 'a'
    B = 'b'

    @classmethod
    def get_readable_value(cls, choice):
        return cls(choice).value.upper()


# Enum with custom objects as values
class Value:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class CustomObjectEnum(Enum):
    A = Value(1)
    B = Value('B')


# Enum with autogenerated values
class AutoEnum(Enum):
    A = auto()  # 1
    B = auto()  # 2


class CustomAutoEnumValueGenerator(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return {
            'A': 'foo',
            'B': 'bar'
        }[name]


class CustomAutoEnum(CustomAutoEnumValueGenerator):
    A = auto()
    B = auto()
