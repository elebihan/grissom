==============
grissom-origin
==============

------------------------------------------------
Search the source code which generated a program
------------------------------------------------

:Author: Eric Le Bihan <eric.le.bihan.dev@free.fr>
:Copyright: 2013 Eric Le Bihan
:Manual section: 1

SYNOPSIS
========

grissom-origin [OPTIONS] <file>, [file, ...]

DESCRIPTION
===========

`grissom-origin` searches for the source code which generated the binary
executable files or shared libraries passed as argument.

`grissom-origin` can read from standard input if '-' is used as the first
argument.

OPTIONS
=======

-I DIR, --include DIR         set source code search path
-Q, --quiet                   be quiet
-S CMD, --strip CMD           set command to discard symbols

.. vim: ft=rst
