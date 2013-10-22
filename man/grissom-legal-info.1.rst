==================
grissom-legal-info
==================

-----------------------------------
Find legal information about a file
-----------------------------------

:Author: Eric Le Bihan <eric.le.bihan.dev@free.fr>
:Copyright: 2013 Eric Le Bihan
:Manual section: 1

SYNOPSIS
========

grissom-legal-info [OPTIONS] <command> [<argument>, ...]

grissom-legal-info [OPTIONS] analyze <file> [<file>, ...]

grissom-legal-info [OPTIONS] query <package> [<package>, ...]

grissom-legal-info [OPTIONS] spdx <package>

grissom-legal-info [OPTIONS] search <pattern>

grissom-legal-info submit <file> [<file>, ...]

DESCRIPTION
===========

`grissom-legal-info` searches for the legal information about a file, using
Fossology.

At start-up, the program looks for configuration parameters from
``~/.config/grissom.conf``. Some of these parameters can be overriden using
options on the command line.

For some commands, `grissom-legal-info` can read from standard input if '-' is
used as the first argument.

OPTIONS
=======

-C, --secured           use a secured connection
-P P, --password P      set user passsword
-S A, --server A        set server address
-U N, --user N          set user name

COMMANDS
========

The following commands are understood:

analyze <file>, [file, ...]
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Report the licenses of the files passed as arguments. If *--spdx* is set and
*file* is an archive (tar, gzip,...) then the output will be formatted in the
Software Package Data eXchange format (see http://spdx.org/).

Available options:

-s, --spdx    output result in SPDX format

Examples:

  $ grissom-legal-info analyze /path/to/frob/src/main.c

  $ grissom-legal-info analyze --spdx /path/to/baz-2.0.tar.xz

query <file>, [file, ...]
~~~~~~~~~~~~~~~~~~~~~~~~~~

Query the licenses of the packages passed as arguments.

Note that the wildcard character '%' is allowed, but then only the licenses of
the first matching package will be reported.

Available options:

-f, --full    output licenses of all the files

Example:

  $ grissom-legal-info query foo-1.0.0.tar.gz

search <pattern>
~~~~~~~~~~~~~~~~

Search for packages available in Fossology server. Use the '%' character as a
wildcard in *pattern*. If *--details* is set, the upload ID and the item ID
will be reported, as well as the name.

Options:

-d, --details   show details

Example:

  $ grissom-legal-info search foo%.tar.gz

spdx <package>
~~~~~~~~~~~~~~

Create a SPDX file for a package registered in Fossology. The output is
formatted as tag/value lines.

Options:

-a N, --author N    set author of the document
-c C, --comment C   add a comment
-o F, --output F    set output file

Example:

  $ grissom-legal-info -a 'Elmer Fudd' foo-1.0.0.tar.gz

submit <file> [<file>, ...]
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Submit a file to Fossology for analysis and storage.

Example:

  $ grissom-legal-info submit /path/to/frob-3.3.tar.gz

SEE ALSO
========

- ``grissom.conf(5)``

.. vim: ft=rst
