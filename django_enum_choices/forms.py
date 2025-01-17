from django import forms

from .choice_builders import value_value
from .utils import as_choice_builder, value_from_built_choice, build_enum_choices


class EnumChoiceField(forms.ChoiceField):
    def __init__(self, enum_class, choice_builder=value_value, **kwargs):
        self.enum_class = enum_class
        self.choice_builder = as_choice_builder(choice_builder)

        kwargs['choices'] = self.build_choices()

        super().__init__(**kwargs)

    def build_choices(self):
        return build_enum_choices(
            self.enum_class,
            self.choice_builder
        )

    def _enum_from_input_value(self, value):
        for choice in self.enum_class:
            if value_from_built_choice(self.choice_builder(choice)) == value:
                return choice

    def to_python(self, value):
        if value is None:
            return

        if value in self.empty_values:
            return ''

        return self._enum_from_input_value(value) or value

    def valid_value(self, value):
        return value in self.enum_class
