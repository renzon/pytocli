# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from collections import OrderedDict

from six import with_metaclass


class OptionFactory(object):
    """Base class for all option factories. Must be extended"""

    def __init__(self, name, cmd):
        self.cmd = cmd
        self.name = name
        self.values = []

    def __str__(self):
        """abstract so subclasses can be aware about overriding it"""
        raise NotImplementedError()

    def __repr__(self):
        return '{} Option with name {} and value {!r}'.format(
            type(self).__name__, self.name, self.values)

    def add_values(self, *values):
        """Concrete classes need to decide when adding values is possible"""
        raise NotImplementedError()

    def __call__(self, *values):
        self.add_values(*values)
        return self.cmd


class NoValueOption(OptionFactory):
    """Base class for all options which have no value . Must be extended"""

    def add_values(self, *values):
        if len(values) > 0:
            raise ValueError(
                'option {} does not accept any value. value(s): {}'.format(
                    self.name, self.values)
            )

    def __str__(self):
        return self.name


class SingleValueOption(OptionFactory):
    """Base class for all options which have exactly one value. Must be
    extended"""

    def add_values(self, *values):
        if len(values) != 1 or len(self.values) != 0:
            raise ValueError(
                'option {} must have exactly one value, {} given: {}'.format(
                    self.name, len(self.values), self.values
                )
            )
        self.values.extend(values)

    def __str__(self):
        return '{} {}'.format(self.name, self.values[0])


class MultiValuesOption(OptionFactory):
    """Base class for all options which have exactly one value. Must be
    extended"""
    values_separator = ' '

    def add_values(self, *values):
        if len(values) == 0 and len(self.values) == 0:
            raise ValueError(
                'option {} must have exactly at least one value'.format(
                    self.name)
            )
        self.values.extend(values)

    def __str__(self):
        values_str = self.values_separator.join(map(str, self.values))
        return '{} {}'.format(self.name, values_str)


class Option(object):
    """Class to add options to Commands"""
    instances_counter = 0

    def __init__(self, option_factory, option_name, doc='No doc provided'):
        self.option_name = option_name
        type(self).instances_counter += 1
        self.doc = doc
        self.count = self.instances_counter
        self.option_factory = option_factory
        self._attr = None

    def _set_attr_name(self, name):
        self._attr = name

    def __get__(self, instance, owner):
        # if has no instance, this is a class access. Returning self to
        # provide useful repr
        if instance is None:
            return self
        if self._attr not in instance.current_options:
            instance.current_options[self._attr] = self.option_factory(
                self.option_name, instance)
        return instance.current_options[self._attr]

    def __repr__(self):
        return 'Option {}: {}'.format(self.option_name, self.doc)


class SubCommand(object):
    """Class to add SubCommands to Commands"""
    instances_counter = 0

    def __init__(self, cmd_factory):
        type(self).instances_counter += 1
        self.count = self.instances_counter
        self.cmd_factory = cmd_factory
        self.name = None

    def _set_cmd_attr_name(self, name):
        self._attr = name

    def __get__(self, instance, owner):
        # if has no instance, return instance with generic object for
        # documentation purpose
        if instance is None:
            return self.cmd_factory(object())
        return self.cmd_factory(instance)

    def __repr__(self):
        return 'SubCommand {}: {}'.format(
            self.cmd_factory.name,
            self.cmd_factory.__doc__ or 'No doc provided')


class _CommandMeta(type):
    """metaclass to build Command options and subcommands"""

    def __new__(cls, class_to_be_created_name, bases, attrs):
        def set_descriptor_attr_name(descriptor, name):
            descriptor._set_attr_name(name)
            return descriptor

        options = [
            set_descriptor_attr_name(attr_value, attr_name)
            for attr_name, attr_value in attrs.items()
            if hasattr(attr_value, '_set_attr_name')
            ]
        options.sort(key=lambda op: op.count)

        def set_descriptor_cmd_attr_name(descriptor, name):
            descriptor._set_cmd_attr_name(name)
            return descriptor

        sub_commands = [set_descriptor_cmd_attr_name(attr_value, attr_name)
                        for attr_name, attr_value in attrs.items()
                        if hasattr(attr_value, '_set_cmd_attr_name')]
        sub_commands.sort(key=lambda op: op.count)

        attrs['options'] = tuple(op._attr for op in options)
        attrs['sub_commands'] = tuple(sub._attr for sub in sub_commands)

        return super(_CommandMeta, cls).__new__(cls, class_to_be_created_name,
                                                bases, attrs)


class CommandBuilder(with_metaclass(_CommandMeta)):
    name = ''
    options = tuple()  # going to be filled by _CommandMeta
    sub_commands = tuple()  # going to be filled by _CommandMeta

    def __init__(self):
        self.current_options = OrderedDict()  # options added to command
        # instance

    def __str__(self):
        if len(self.current_options) == 0:
            return self.name
        options_str = ' '.join(map(str, self.current_options.values()))
        return ' '.join((self.name, options_str))

    def __repr__(self):
        return 'CommandBuilder {}: {}'.format(
            self.name,
            self.__doc__ or 'No doc provided')


class SubCommandBuilder(CommandBuilder):
    def __init__(self, parent_cmd):
        super(SubCommandBuilder, self).__init__()
        self.parent_cmd = parent_cmd

    def __str__(self):
        return '{} {}'.format(
            self.parent_cmd,
            super(SubCommandBuilder, self).__str__()
        )

    def __repr__(self):
        return 'SubCommandBuilder {}: {}'.format(
            self.name,
            self.__doc__ or 'No doc provided')
