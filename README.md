# django-enum-choices

A custom Django choice field to use with [Python enums.](https://docs.python.org/3/library/enum.html)

[![PyPI version](https://badge.fury.io/py/django-enum-choices.svg)](https://badge.fury.io/py/django-enum-choices)

## Table of Contents
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Customizing readable values](#customizing-readable-values)
- [Usage with forms](#usage-with-forms)
- [Postgres ArrayField Usage](#postgres-arrayfield-usage)
- [Usage with Django Rest Framework](#usage-with-django-rest-framework)
  - [Caveat](#caveat)
- [Serializing PostgreSQL ArrayField](#serializing-postgresql-arrayfield)
- [Implementation details](#implementation-details)
- [Using Python's `enum.auto`](#using-pythons-enumauto)
- [Development](#development)

## Installation

```bash
pip install django-enum-choices
```

## Basic Usage

```python
from django.db import models

from django_enum_choices.fields import EnumChoiceField


from enum import Enum

class MyEnum(Enum):
    A = 'a'
    B = 'b'


class MyModel(models.Model):
    enumerated_field = EnumChoiceField(MyEnum)
```

**Model creation**

```python
instance = MyModel.objects.create(enumerated_field=MyEnum.A)
```

**Changing enum values**

```python
instance.enumerated_field = MyEnum.B
instance.save()
```

**Filtering**

```python
MyModel.objects.filter(enumerated_field=MyEnum.A)
```

## Customizing readable values
If a `choice_builder` argument is passed to a model's `EnumChoiceField`, `django_enum_choices` will use it to generate the choices.
The `choice_builder` must be a callable that accepts an enumeration choice and returns a tuple,
containing the value to be saved and the readable value.
By default `django_enum_choices` uses one of the four choice builders defined in `django_enum_choices.choice_builders`, named `value_value`.
It returns a tuple containing the enumeration's value twice:
```python
from django_enum_choices.choice_builders import value_value

class MyEnum(Enum):
    A = 'a'
    B = 'b'

print(value_value(MyEnum.A))  # ('a', 'a')
```

You can use one of the existing ones that fits your needs:

```python
from django_enum_choices.choice_builders import attribute_value

class MyEnum(Enum):
    A = 'a'
    B = 'b'

class CustomReadableValueEnumModel(models.Model):
    enumerated_field = EnumChoiceField(
        MyEnum,
        choice_builder=attribute_value
    )
```

The resulting choices for `enumerated_field` will be `(('A', 'a'), ('B', 'b'))`


You can also define your own choice builder:

```python
class MyEnum(Enum):
    A = 'a'
    B = 'b'

def choice_builder(choice):
    return choice.value, choice.value.upper() + choice.value

class CustomReadableValueEnumModel(models.Model):
    enumerated_field = EnumChoiceField(
        MyEnum,
        choice_builder=choice_builder
    )
```

Which will result in the following choices `(('a', 'Aa'), ('b', 'Bb'))`

The values in the returned from `choice_builder` tuple will be cast to strings before being used.


## Usage with forms

**Usage with `django.forms.Form`**

```python
from django_enum_choices.forms import EnumChoiceField

from .enumerations import MyEnum

class StandardEnumForm(forms.Form):
    enumerated_field = EnumChoiceField(MyEnum)

form = StandardEnumForm({
    'enumerated_field': 'a'
})
form.is_valid()

print(form.cleaned_data)  # {'enumerated_field': <MyEnum.A: 'a'>}
```

**Usage with `django.forms.ModelForm`**

```python
from .models import MyModel

class ModelEnumForm(forms.ModelForm):
    class Meta:
        model = MyModel
        fields = ['enumerated_field']

form = ModelEnumForm({
    'enumerated_field': 'a'
})

form.is_valid()

print(form.save(commit=True))  # <MyModel: MyModel object (12)>
```

A `choice_builder` argument can be passed to `django_model_choices.forms.EnumChoiceField`
for usage with model fields with custom choice builders:

```python
from .enumerations import MyEnum

def custom_choice_builder(choice):
    return 'Custom_' + choice.value, choice.value

class CustomChoiceBuilderEnumForm(forms.Form):
    enumerated_field = EnumChoiceField(
        MyEnum,
        choice_builder=custom_choice_builder
    )

form = CustomChoiceBuilderEnumForm({
    'enumerated_field': 'Custom_a'
})

form.is_valid()

print(form.cleaned_data)  # {'enumerated_field': <MyEnum.A: 'a'>}
```

## Postgres ArrayField Usage

```python
from django.db import models
from django.contrib.postgres.fields import ArrayField

from django_enum_choices.fields import EnumChoiceField

from enum import Enum

class MyEnum(Enum):
    A = 'a'
    B = 'b'

class MyModelMultiple(models.Model):
    enumerated_field = ArrayField(
        base_field=EnumChoiceField(MyEnum)
    )
```

**Model Creation**

```python
instance = MyModelMultiple.objects.create(enumerated_field=[MyEnum.A, MyEnum.B])
```

**Changing enum values**

```python
instance.enumerated_field = [MyEnum.B]
instance.save()
```

## Usage with Django Rest Framework

**Using a subclass of `serializers.Serializer`**

```python
from rest_framework import serializers

from django_enum_choices.serializers import EnumChoiceField

class MySerializer(serializers.Serializer):
    enumerated_field = EnumChoiceField(MyEnum)

# Serialization:
serializer = MySerializer({
    'enumerated_field': MyEnum.A
})
data = serializer.data  # {'enumerated_field': 'a'}

# Deserialization:
serializer = MySerializer(data={
    'enumerated_field': 'a'
})
serializer.is_valid()
data = serializer.validated_data  # OrderedDict([('enumerated_field', <MyEnum.A: 'a'>)])
```

**Using a subclass of `serializers.ModelSerializer`**

```python
from rest_framework import serializers

from django_enum_choices.serializers import EnumChoiceField

class MyModelSerializer(serializers.ModelSerializer):
    enumerated_field = EnumChoiceField(MyEnum)

    class Meta:
        model = MyModel
        fields = ('enumerated_field', )

# Serialization:
instance = MyModel.objects.create(enumerated_field=MyEnum.A)
serializer = MyModelSerializer(instance)
data = serializer.data  # {'enumerated_field': 'a'}

# Saving:
serializer = MyModelSerializer(data={
    'enumerated_field': 'a'
})
serializer.is_valid()
serializer.save()
```

**Additionally, a `choice_builder` argument can be passed to the serializer field** for custom choice generation:
```python
def custom_choice_builder(choice):
    return 'Custom_' + choice.value, choice.value

class CustomChoiceBuilderSerializer(serializers.Serializer):
    enumerted_field = EnumChoiceField(
        MyEnum,
        choice_builder=custom_choice_builder
    )

serializer = CustomChoiceBuilderSerializer({
    'enumerated_field': MyEnum.A
})

data = serializer.data # {'enumerated_field': 'Custom_a'}
```

When using the `EnumChoiceModelSerializerMixin` with DRF's `serializers.ModelSerializer`, the `choice_builder` is automatically passed from the model field to the serializer field.

### Caveat

If you don't explicitly specify the `enumerated_field = EnumChoiceField(MyEnum)`, then you need to include the `EnumChoiceModelSerializerMixin`:

```python
from rest_framework import serializers

from django_enum_choices.serializers import EnumChoiceModelSerializerMixin

class ImplicitMyModelSerializer(
    EnumChoiceModelSerializerMixin,
    serializers.ModelSerializer
):
    class Meta:
        model = MyModel
        fields = ('enumerated_field', )
```

By default `ModelSerializer.build_standard_field` coerces any field that has a model field with choices to `ChoiceField` which returns the value directly.

Since enum values resemble `EnumClass.ENUM_INSTANCE` they won't be able to be encoded by the `JSONEncoder` when being passed to a `Response`.

That's why we need the mixin.

## Serializing PostgreSQL ArrayField
`django-enum-choices` exposes a `MultipleEnumChoiceField` that can be used for serializing arrays of enumerations.

**Using a subclass of `serializers.Serializer`**

```python
from rest_framework import serializers

from django_enum_choices.serializers import MultipleEnumChoiceField

class MultipleMySerializer(serializers.Serializer):
    enumerated_field = MultipleEnumChoiceField(MyEnum)

# Serialization:
serializer = MultipleMySerializer({
    'enumerated_field': [MyEnum.A, MyEnum.B]
})
data = serializer.data  # {'enumerated_field': ['a', 'b']}

# Deserialization:
serializer = MultipleMySerializer(data={
    'enumerated_field': ['a', 'b']
})
serializer.is_valid()
data = serializer.validated_data  # OrderedDict([('enumerated_field', [<MyEnum.A: 'a'>, <MyEnum.B: 'b'>])])
```

**Using a subclass of `serializers.ModelSerializer`**

```python
class ImplicitMultipleMyModelSerializer(
    EnumChoiceModelSerializerMixin,
    serializers.ModelSerializer
):
    class Meta:
        model = MyModelMultiple
        fields = ('enumerated_field', )

# Serialization:
instance = MyModelMultiple.objects.create(enumerated_field=[MyEnum.A, MyEnum.B])
serializer = ImplicitMultipleMyModelSerializer(instance)
data = serializer.data  # {'enumerated_field': ['a', 'b']}

# Saving:
serializer = ImplicitMultipleMyModelSerializer(data={
    'enumerated_field': ['a', 'b']
})
serializer.is_valid()
serializer.save()
```

The `EnumChoiceModelSerializerMixin` does not need to be used if `enumerated_field` is defined on the serializer class explicitly.


## Implementation details

* `EnumChoiceField` is a subclass of `CharField`.
* Only subclasses of `Enum` are valid arguments for `EnumChoiceField`.
* `max_length`, if passed, is ignored. `max_length` is automatically calculated from the longest choice.
* `choices` are generated using a special `choice_builder` function, which accepts an enumeration and returns a tuple of 2 items.
  * Four choice builder functions are defined inside `django_enum_choices.choice_builders`
  * By default the `value_value` choice builder is used. It produces the choices from the values in the enumeration class, like `(enumeration.value, enumeration.value)`
  * `choice_builder` can be overriden by passing a callable to the `choice_builder` keyword argument of `EnumChoiceField`.
  * All values returned from the choice builder **will be cast to strings** when generating choices.

For example, lets have the following case:

```python
class Value:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class CustomObjectEnum(Enum):
    A = Value(1)
    B = Value('B')

	# The default choice builder `value_value` is being used

class SomeModel(models.Model):
    enumerated_field = EnumChoiceField(CustomObjectEnum)
```

We'll have the following:

* `SomeModel.enumerated_field.choices == (('1', '1'), ('B', 'B'))`
* `SomeModel.enumerated_field.max_length == 3`

## Using Python's `enum.auto`
`enum.auto` can be used for shorthand enumeration definitions:

```python
from enum import Enum, auto

class AutoEnum(Enum):
    A = auto()  # 1
    B = auto()  # 2

class SomeModel(models.Model):
    enumerated_field = EnumChoiceField(Enum)
```

This will result in the following:
* `SomeModel.enumerated_field.choices == (('1', '1'), ('2', '2'))`

**Overridinng `auto` behaviour**
Custom values for enumerations, created by `auto`, can be defined by
subclassing an `Enum` that defines `_generate_next_value_`:

```python
class CustomAutoEnumValueGenerator(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return {
            'A': 'foo',
            'B': 'bar'
        }[name]


class CustomAutoEnum(CustomAutoEnumValueGenerator):
    A = auto()
    B = auto()
```

The above will assign the values mapped in the dictionary as values to attributes in `CustomAutoEnum`.

## Development
**Prerequisites**
* SQLite3
* PostgreSQL server
* Python >= 3.5 virtual environment

```bash
git clone https://github.com/HackSoftware/django-enum-choices.git
cd django_enum_choices
pip install -e .[dev]
```

Linting and running the tests:
```bash
tox
```
