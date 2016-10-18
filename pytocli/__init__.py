# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from collections import OrderedDict

__version__ = '0.1'


class Option(object):
    """Base class for all option. Must be extended"""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        """abstract so subclasses can be aware about overriding it"""
        raise NotImplementedError()

    def __repr__(self):
        return '{} with name {}'.format(type(self), self.name)

    def add_value(self, value):
        """Concrete classes need to decide when adding value is possible"""
        raise ValueError('Option {} accepts no value'.format(self.name))


class ValueOption(Option):
    """Base class for all options which have exactly one value.
    Must be extended
    """

    def __init__(self, name):
        super(ValueOption, self).__init__(name)
        self.value = None

    def add_value(self, value):
        if self.value is not None:
            tmpl = ('option {} has already value {} which can not be '
                    'overwritten by {}')
            raise ValueError(tmpl.format(self.name, self.value, value))
        self.value = str(value)

    def __repr__(self):
        return '{} with name {} and value {!r}'.format(
            type(self), self.name, self.value
        )


class MultiValuesOption(Option):
    """Base class for all options which have can have multiple values.
    Must be extended
    """

    def __init__(self, name):
        super(MultiValuesOption, self).__init__(name)
        self.values = []

    def add_value(self, value):
        self.values.append(str(value))

    def _values_str(self):
        return ' '.join(self.values)

    def __repr__(self):
        return '{} with name {} and values {!r}'.format(
            type(self), self.name, self.values)


class DashedOption(Option):
    def __str__(self):
        return '-%s' % self.name


class DoubleDashedOption(Option):
    def __str__(self):
        return '--%s' % self.name


class DashedValueOption(ValueOption):
    def __str__(self):
        return '-{} {}'.format(self.name, self.value)


class DoubleDashedValueOption(ValueOption):
    def __str__(self):
        return '--{} {}'.format(self.name, self.value)


class DashedMultiValueOption(MultiValuesOption):
    def __str__(self):
        return '-{} {}'.format(self.name, self._values_str())


class DoubleDashedMultiValueOption(MultiValuesOption):
    def __str__(self):
        return '--{} {}'.format(self.name, self._values_str())


class CommandBuilder(object):
    """Base clas for all commands"""

    name = ''

    def __init__(self):
        self.options = OrderedDict()

    def _add_option(self, cls, option):
        if option in self.options:
            raise ValueError(
                'option {} is already present'.format(self.options[option]))
        self.options[option] = cls(option)
        return self

    def _add_value_option(self, cls, option, *values):
        if len(values) == 0:
            raise ValueError('option %s need at least on value' % option)
        if option not in self.options:
            self.options[option] = cls(option)
        option_obj = self.options[option]
        for v in values:
            option_obj.add_value(v)
        return self

    def dashed_option(self, option):
        """Add dashed option to command.

        :param option: str indication the option name
        """
        return self._add_option(DashedOption, option)

    def double_dashed_option(self, option):
        """Add double dashed option to command.

        :param option: str indication the option name
        """
        return self._add_option(DoubleDashedOption, option)

    def dashed_value_option(self, option, value):
        """Add dashed option with value"""
        return self._add_value_option(DashedValueOption, option, value)

    def double_dashed_value_option(self, option, value):
        """Add double dashed option with value"""
        return self._add_value_option(DoubleDashedValueOption, option, value)

    def dashed_multi_value_option(self, option, *values):
        """Add dashed option with multiple values"""
        return self._add_value_option(DashedMultiValueOption, option, *values)

    def double_dashed_multi_value_option(self, option, *values):
        """Add double dashed option with multiple values"""
        return self._add_value_option(DoubleDashedMultiValueOption, option,
                                      *values)

    def __repr__(self):
        if not self.options:
            return self.name
        options_str = ' '.join(map(str, self.options.values()))
        return ' '.join((self.name, options_str))


class SubCommandBuilder(CommandBuilder):
    def __init__(self, parent_cmd):
        super(SubCommandBuilder, self).__init__()
        self.parent_cmd = parent_cmd

    def __str__(self):
        return '{} {}'.format(
            self.parent_cmd,
            super(SubCommandBuilder, self).__str__(),
        )
