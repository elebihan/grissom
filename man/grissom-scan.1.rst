============
grissom-scan
============

--------------------------------------------
Scan a directory for binary executable files
--------------------------------------------

:Author: Eric Le Bihan <eric.le.bihan.dev@free.fr>
:Copyright: 2013 Eric Le Bihan
:Manual section: 1

SYNOPSIS
========

grissom-scan [OPTIONS] <directory>

DESCRIPTION
===========

`grissom-scan` scans a directory recursively, looking for binary executable
file and/or shared libraries and kernel modules.

OPTIONS
=======

-l, --include-libs        include shared libraries
-m, --include-kmods       include kernel modules

.. vim: ft=rst
