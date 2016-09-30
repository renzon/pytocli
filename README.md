# pytocli

A Python lib to generate CLI commands
 
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

```python
>>> from pytocli.example.git.Git
>>> str(Git())
'git'
>>> str(Git().p())
'git'
>>> str(Git().v())
'git -v'
>>> str(Git().p().v())
'git -p -v'
>>> help(Git.p)
'insert -p option which paginates result'
>>> help(Git.p)
'insert -v to verbose mode'
```
