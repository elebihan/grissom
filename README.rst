============================================
Grissom - FOSS Compliance Toolkit, CSI Style
============================================

Description
===========

Grissom is a set of programs to help check the FOSS compliance of a project,
in a CSI way. Most of them deal with inspecting binary files (programs or
shared libraries) or gathering licensing/copyright information. On Unix
platforms, they can be combined using pipes.

See the MAN pages for further documentation.

System Requirements
===================

- Python 3.x
- external tools needed by `grissom-autopsy(1)`:

  * cramfs tools

Installation
============

To install the programs and modules::

  $ python3 setup.py install
