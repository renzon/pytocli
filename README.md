# pytocli

A Python lib to generate CLI commands

[![Travis Status](https://travis-ci.org/renzon/pytocli.svg?branch=master)](https://coveralls.io/github/renzon/pytocli?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/renzon/pytocli/badge.svg?branch=master)](https://travis-ci.org/renzon/pytocli)
[![Updates](https://pyup.io/repos/github/renzon/pytocli/shield.svg)](https://pyup.io/repos/github/renzon/pytocli/) 
## Problem

You need generate some CLI commands and start simple as
```python
>>> def git():
...    return 'git'
>>> git()
'git'

```
But you realize it has many options:`

```python
>>> def git(p=None, v=None):
...    cmd = 'git' 
...    if p:
...        cmd += ' -p'
...    if v is not None:
...        cmd += ' -v'
...    return cmd
>>> git()
'git'
>>> git(p=True)
'git -p'
>>> git(v=True)
'git -v'
>>> git(p=True, v=True)
'git -p -v'

```
So the spaghetti code begins.

# Lib Goal

The lib goal is provide a fluent interface to generate cli commands:

```python
>>> from tests.test_pytocli import Git
>>> str(Git())
'git'
>>> str(Git().paginate())
'git -p'
>>> str(Git().help())
'git --help'
>>> str(Git().paginate().help())
'git -p --help'
>>> str(Git().paginate().help().commit().message('bar'))
'git -p --help commit -m bar'

```

## How to extend the framework. Use Case: git like

### Step 1: inherit from CommandBuilder class

The command name must be overwritten as class attribute.
 
```python
from pytocli import CommandBuilder


class Git(CommandBuilder):
    name = 'git'
```

## Step 2: create command option with aux methods
 
```python
from pytocli import CommandBuilder


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
        return self.double_dashed_value_option('exec_path', value)

    def fake(self, *values):
        return self.dashed_multi_value_option('fake', *values)

    def dfake(self, *values):
        return self.double_dashed_multi_value_option('dfake', *values)

```
## Step 3: create a subcomman following steps 1 and 2
 
```python
from pytocli import SubCommandBuilder


class Commit(SubCommandBuilder):
    name = 'commit'

    def message(self, msg):
        return self.dashed_value_option('m', msg)
```

## Step 4: create method on CommandBuilder connecting it with SubCommandBuilder
 
```python
class Git(CommandBuilder):
    name = 'git'

    #other methods are hidden
    
    def commit(self):
        return Commit(self)
```

## Step 5: Add parameters to Parent command

Passing parameters to parent command can be done even after subcommand creation:
 
```python
>>> commit = Git().commit()
>>> str(commit)
'git commit'
>>> commit.parent_cmd
git
>>> commit.parent_cmd.paginate()
git -p
>>> str(commit)
'git -p commit'

```

property can be used to create more semantic command:
 
```python
class Commit(SubCommandBuilder):
    name = 'commit'

    @property
    def git(self):
        return self.parent_cmd
```
So the command can be:

```python
>>> commit = Git().commit()
>>> str(commit)
'git commit'
>>> commit.git
git
>>> commit.git.paginate()
git -p
>>> str(commit)
'git -p commit'

```
