# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import pytest

from pytocli import (CommandBuilder, Option, NoValueOption, SingleValueOption,
                     MultiValuesOption, SubCommandBuilder, SubCommand)
from pytocli._base import OptionFactory


class GitSubCommand(SubCommandBuilder):
    @property
    def git(self):
        return self.parent_cmd


class Commit(GitSubCommand):
    """git commit sub command"""
    name = 'commit'
    message = Option(SingleValueOption, '-m', 'Message to be added on commit')


class Revert(GitSubCommand):
    name = 'revert'


class Git(CommandBuilder):
    name = 'git'
    # Options
    verbose = Option(NoValueOption, '-v', 'Verbose mode')
    start = Option(SingleValueOption, '-C')
    multi = Option(MultiValuesOption, '--mu')

    # SubCommands
    commit = SubCommand(Commit)
    revert = SubCommand(Revert)


def test_simple_command():
    assert 'git' == str(Git())


def test_no_value():
    assert 'git -v' == str(Git().verbose())

def test_no_value_can_not_receive_value():
    with pytest.raises(ValueError):
        Git().verbose('foo')


def test_single_value():
    assert 'git -C foo.git' == str(Git().start('foo.git'))


def test_single_values_with_no_arg():
    with pytest.raises(ValueError):
        Git().start()


def test_single_values_with_2_args():
    with pytest.raises(ValueError):
        Git().start(1, 2)


def test_single_values_adding_2_args_on_consecutive_calls():
    with pytest.raises(ValueError):
        Git().start(1).start(2)


def test_multivalue():
    cmd = Git()
    assert 'git --mu 1 2' == str(cmd.multi(1, 2))
    assert 'git --mu 1 2 3' == str(cmd.multi(3))


def test_chaining():
    assert 'git -v -C foo.git' == str(Git().verbose().start('foo.git'))


def test_doc_on_repr():
    assert 'Option -v: Verbose mode' == repr(Git.verbose)
    assert 'Option --mu: No doc provided' == repr(Git.multi)


def test_options_tuple():
    assert ('verbose', 'start', 'multi') == Git.options


def test_simple_sub_command():
    assert 'git commit' == str(Git().commit)


def test_chaining_sub_command():
    assert ('git -v commit -m "a great msg"' ==
            str(Git().verbose().commit.message('"a great msg"')))


def test_add_option_to_parent():
    commit = Git().commit
    assert ('git commit -m "a great msg"' ==
            str(commit.message('"a great msg"')))
    commit.git.verbose()
    assert 'git -v commit -m "a great msg"' == str(commit)


def test_sub_commands_tuple():
    assert ('commit', 'revert') == Git.sub_commands


def test_option_factory_str_is_abstract():
    with pytest.raises(NotImplementedError):
        str(OptionFactory('foo', 'foo'))


def test_option_factory_repr():
    assert ('OptionFactory Option with name foo and value []' ==
            repr(OptionFactory('foo', 'bar')))


def test_option_factory_add_values_is_abstract():
    with pytest.raises(NotImplementedError):
        OptionFactory('foo', 'foo').add_values()
