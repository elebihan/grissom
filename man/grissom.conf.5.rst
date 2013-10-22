============
grissom.conf
============

------------------------------
Configuration file for Grissom
------------------------------

:Author: Eric Le Bihan <eric.le.bihan.dev@free.fr>
:Copyright: 2013 Eric Le Bihan
:Manual section: 5

DESCRIPTION
===========

The ``grissom.conf`` file contains the configuration parameters for various
tools from grissom, like `grissom-legal-info(1)`. It uses a structure
similar to Microsoft Windows INI files.

The default location for this file is ``~/.config/grissom.conf``.

SYNTAX
======

The file contains sections, led by a *[section]* header followed by
*key=value* pairs. Lines beginning with '#' are considered as comments.

Example::

  # Configuration file
  [Fossology]
  ServerAddress=fossologyspdx.ist.unomaha.edu
  ConnectionSecured=true
  User=homer
  Password=secret

SECTIONS
========

Here is the list of mandatory sections.

Fossology
---------

* ServerAddress: address of the Fossology server to use.
* ConnectionSecured: if true, use a secured connection.
* User: name to use for connection.
* Password: password for the user.

SEE ALSO
========

- ``grissom-legal-info(1)``

.. vim: ft=rst
