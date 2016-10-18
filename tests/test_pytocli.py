# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import pytest

from pytocli import CommandBuilder, SubCommandBuilder


class Git(CommandBuilder):
    name = 'git'

    def paginate(self):
        """Add paginate option to git command

        :return: CommandBuilder for chaining calls
        """
        return self.dashed_option('p')

    def help(self):
        """Add help option to git command

        :return: CommandBuilder for chaining calls
        """
        return self.double_dashed_option('help')

    def start(self, value):
        return self.dashed_value_option('C', value)

    def exec_path(self, value):
        return self.double_dashed_value_option('exec_path-path', value)

    def fake(self, *values):
        return self.dashed_multi_value_option('fake', *values)

    def dfake(self, *values):
        return self.double_dashed_multi_value_option('dfake', *values)

    def commit(self):
        return Commit(self)


class Commit(SubCommandBuilder):
    name = 'commit'

    @property
    def git(self):
        return self.parent_cmd

    def message(self, msg):
        return self.dashed_value_option('m', msg)


def test_simple_command():
    assert 'git' == str(Git())


def test_dashed_option():
    assert 'git -p' == str(Git().dashed_option('p'))
    assert 'git -p' == str(Git().paginate())


def test_dashed_option_duplicated():
    cmd = Git().paginate()
    with pytest.raises(ValueError):
        cmd.paginate()


def test_double_dashed_option():
    assert 'git --help' == str(Git().double_dashed_option('help'))


def test_double_dashed_option_duplicated():
    cmd = Git().double_dashed_option('help')
    with pytest.raises(ValueError):
        cmd.double_dashed_option('help')


def test_dashed_value_option():
    assert 'git -C foo.git' == str(Git().dashed_value_option('C', 'foo.git'))
    assert 'git -C foo.git' == str(Git().start('foo.git'))


def test_dashed_value_option_duplicated():
    cmd = Git().start('foo.git')
    with pytest.raises(ValueError):
        cmd.start('bar.git')


def test_double_dashed_value_option():
    assert ('git --exec_path-path /usr/bin/git' ==
            str(Git().double_dashed_value_option('exec_path-path', '/usr/bin/git')))
    assert 'git --exec_path-path /usr/bin/git' == str(Git().exec_path('/usr/bin/git'))


def test_double_dashed_value_option_duplicated():
    cmd = Git().exec_path('foo')
    with pytest.raises(ValueError):
        cmd.exec_path('bar')


def test_dashed_with_multiple_values():
    assert 'git -fake 1 2 3' == str(Git().fake(1, 2, 3))
    cmd = Git().fake(1)
    assert 'git -fake 1' == str(cmd)
    assert 'git -fake 1 2' == str(cmd.fake(2))
    assert 'git -fake 1 2 3' == str(cmd.fake(3))


def test_dashed_missing_value():
    with pytest.raises(ValueError):
        Git().fake()


def test_double_dashed_with_multiple_values():
    assert 'git --dfake 1 2 3' == str(Git().dfake(1, 2, 3))
    cmd = Git().dfake(1)
    assert 'git --dfake 1' == str(cmd)
    assert 'git --dfake 1 2' == str(cmd.dfake(2))
    assert 'git --dfake 1 2 3' == str(cmd.dfake(3))


def test_double_dashed_missing_value():
    with pytest.raises(ValueError):
        Git().dfake()


def test_subcommand():
    assert 'git commit' == str(Git().commit())


def test_complete_chaining():
    cmd = Git()
    assert 'git' == str(cmd)
    assert 'git -p' == str(cmd.paginate())
    assert 'git -p --exec_path-path foo' == str(cmd.exec_path('foo'))
    assert 'git -p --exec_path-path foo commit -m bar' == str(
        cmd.commit().message('bar'))
    assert ('git -p commit -m baz' ==
            str(Git().paginate().commit().message('baz')))


def test_parent_command_access():
    commit = Git().commit()
    commit.parent_cmd.paginate()
    assert 'git -p commit' == str(commit)
    commit = Git().commit()
    commit.git.paginate()
    assert 'git -p commit' == str(commit)
