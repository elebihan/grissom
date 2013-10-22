================
grissom-tutorial
================

----------------------------------
A tutorial introduction to Grissom
----------------------------------

:Author: Eric Le Bihan <eric.le.bihan.dev@free.fr>
:Copyright: 2013 Eric Le Bihan
:Manual section: 7

Introduction
============

Grissom is a set of programs to help check the FOSS compliance of a project,
in a CSI way. Most of them deal with inspecting binary files (programs or
shared libraries) or gathering licensing/copyright information. On Unix
platforms, they can be combined using pipes.

Some of the tools may use parameters from the ``~/.config/grissom.conf``
configuration file. For the syntax of this file, see `grissom.conf(5)`.

Binary Files Inspection
=======================

The following programs can gather information from binary files, either
programs, shared libraries or root file system images:

- `grissom-scan(1)`: scan a directory for binary executable files.
- `grissom-deps(1)`: print the shared libraries a program (or a shared library)
  depends on.
- `grissom-origin(1)`: search the source code which generated a program.
- `grissom-autopsy(1)`: inspect and extract contents of binary files.

Here is a usage example, where we want to inspect the content of
``rootfs.cramfs``, the root file system of an embedded system::

  $ grissom-autopsy -o /tmp rootfs.cramfs
  $ grissom-scan /tmp/rootfs | grissom-deps

We can generate a pretty image of the dependencies if we use `dot(1)`::

  $ grissom-scan /tmp/rootfs | \
    grissom-deps -L /tmp/rootfs/usr/lib -L /tmp/rootfs/lib \
    -D | dot -Tpng -o deps.png

If we have access to the build directory of this root file system, we can try
to find out which package generated the programs and libraries embedded. For
example, if it has been built using Buildroot::

  $ grissom-scan /tmp/rootfs | \
    grissom-origin -I /path/to/buildroot/output \
    -S '/path/to/buildroot/output/host/usr/bin/mips-linux-gnu-strip \
        --remove-section=.comment \
        --remove-section=.note \
        -R .note.GNU-stack'

You have to know the options passed to the `strip(1)` program at build time to
perform the search, as `grissom-origin(1)` performs stripping and SHA-1
comparison to identify the source of a binary file.

Legal Information Collection
============================

`grissom-legal-info(1)` can collect legal information (license, copyright)
about a source code package from a `Fossology <http://fossology.org/>`_
server.

Here is an example of collecting the licenses of the programs embedded in the
previous file system::

  $ export BLDDIR=/path/to/buildroot
  $ grissom-scan /tmp/rootfs | \
    grissom-origin -I $BLDDIR/output \
    -S "$BLDDIR/output/host/usr/bin/mips-linux-gnu-strip \
        --remove-section=.comment \
        --remove-section=.note \
        -R \.note.GNU-stack" | \
   sed -e "s,$BLDDIR/,,g" | cut -d: -f2 | cut -d/ -f2 | \
   sort | uniq | grissom-legal-info query -

