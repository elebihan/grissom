============
grissom-deps
============

--------------------------------------
Find linkage dependencies of a program
--------------------------------------

:Author: Eric Le Bihan <eric.le.bihan.dev@free.fr>
:Copyright: 2013 Eric Le Bihan
:Manual section: 1

SYNOPSIS
========

grissom-deps [OPTIONS] <file> [file, ...]

DESCRIPTION
===========

`grissom-deps` search for the linkage dependencies of a program and output
them in various formats:

- simple: output result as an adjacent list.
- pretty: output result as a tree.
- dot: output result in DOT format, to be used with `dot(1)`.

If *-F* option is set, the full path to the dependencies will be printed.

If *-D* option is set, the dependencies will be search recursively. This
option requires the search path for libraries to set using *-L*.

`grissom-deps` can read from standard input if '-' is used as the first
argument.

OPTIONS
=======

-D, --deep                    perform deep search
-F, --full-path               print full pathname
-L PATH, --library-path PATH  set library search path
-f FMT, --format FMT          set output format (simple, pretty, dot)

EXAMPLES
========

To output the dependencies of program `foo` as PNG file::

  $ grissom-deps -L /usr/lib -D -f dot /usr/bin/foo | dot -Tpng -o foo.png

To output the dependencies of all the binary executable files found in
/path/to/target as SVG file::

  $ grissom-scan /path/to/target | grissom-deps -D -f dot | dot -Tsvg -o res.svg

.. vim: ft=rst
